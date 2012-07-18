from cStringIO import StringIO
import base64
import mimetypes
import os
import re

from django.conf.urls.defaults import url
from django.core.files.uploadedfile import InMemoryUploadedFile

from tastypie import fields
from tastypie.authentication import Authentication
from tastypie.bundle import Bundle
from tastypie.utils import trailing_slash

from filer.models import Image

from storybase.api import (DelayedAuthorizationResource,
                           TranslatedModelResource, LoggedInAuthorization)
from storybase_asset.models import (Asset, ExternalAsset, HtmlAsset, 
                                    LocalImageAsset)

class AssetResource(DelayedAuthorizationResource, TranslatedModelResource):
    # Explicitly declare fields that are on the translation model, or the
    # subclass
    title = fields.CharField(attribute='title', blank=True, default='')
    caption = fields.CharField(attribute='caption', blank=True, default='')
    body = fields.CharField(attribute='body', null=True)
    url = fields.CharField(attribute='url', null=True)
    image = fields.FileField(attribute='image', null=True)
    content = fields.CharField(readonly=True)
    # A "write-only" field for specifying the filename when uploading images
    # This is removed from responses to GET requests
    filename = fields.CharField(null=True)

    class Meta:
        always_return_data = True
        queryset = Asset.objects.select_subclasses()
        resource_name = 'assets'
        allowed_methods = ['get', 'post', 'put']
        authentication = Authentication()
        authorization = LoggedInAuthorization()

        delayed_authorization_methods = ['put_detail']

    def get_object_class(self, bundle=None, request=None, **kwargs):
        if bundle.data.get('image', None):
            return LocalImageAsset
        elif bundle.data.get('body', None): 
            return HtmlAsset
        elif bundle.data.get('url', None):
            return ExternalAsset
        else:
            raise AttributeError

    def get_object_list(self, request):
        """
        Get a list of assets, filtering based on the request's user and 
        the publication status
        
        """
        from django.db.models import Q
        # Only show published stories  
        q = Q(status='published')
        if hasattr(request, 'user') and request.user.is_authenticated():
            # If the user is logged in, show their unpublished stories as
            # well
            q = q | Q(owner=request.user)

        return super(AssetResource, self).get_object_list(request).filter(q)

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<asset_id>[0-9a-f]{32,32})%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('dispatch_detail'),
                name="api_dispatch_detail"),
            url(r"^(?P<resource_name>%s)/stories/(?P<story_id>[0-9a-f]{32,32})%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('dispatch_list'),
                name="api_dispatch_list"),
            url(r"^(?P<resource_name>%s)/stories/(?P<story_id>[0-9a-f]{32,32})/sections/none%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('dispatch_list'),
                kwargs={'no_section': True},
                name="api_dispatch_list"),
            url(r"^(?P<resource_name>%s)/sections/(?P<section_id>[0-9a-f]{32,32})%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('dispatch_list'),
                name="api_dispatch_list"),
        ]

    def detail_uri_kwargs(self, bundle_or_obj):
        """
        Given a ``Bundle`` or an object (typically a ``Model`` instance),
        it returns the extra kwargs needed to generate a detail URI.

        This version returns the asset_id field instead of the pk
        """
        kwargs = {}

        if isinstance(bundle_or_obj, Bundle):
            kwargs[self._meta.detail_uri_name] = bundle_or_obj.obj.asset_id
        else:
            kwargs[self._meta.detail_uri_name] = bundle_or_obj.asset_id

        return kwargs

    def parse_data_uri(self, data_uri):
        """
        Parse a data URI string

        Returns a tuple of (mime_type, encoding, data) represented in the URI
        
        See http://tools.ietf.org/html/rfc2397

        """
        pattern = r"data:(?P<mime>[\w/]+);(?P<encoding>\w+),(?P<data>.*)"
        m = re.search(pattern, data_uri)
        return (m.group('mime'), m.group('encoding'), m.group('data'))

    def hydrate_image(self, bundle):
        """Decode the base-64 encoded file"""
        def image_size(f):
            f.seek(0, os.SEEK_END)
            return f.tell()

        image = bundle.data.get('image', None)

        if image:
            (content_type, encoding, data) = self.parse_data_uri(bundle.data['image'])
            filename = bundle.data.get('filename')
            f = StringIO()
            f.write(base64.b64decode(data))
            size = image_size(f)
            image_file = InMemoryUploadedFile(file=f, field_name=None, 
                                              name=filename,
                                              content_type=content_type,
                                              size=size, charset=None)
            image = Image.objects.create(file=image_file)
            bundle.data['image'] = image
            f.close()

        return bundle


    def build_bundle(self, obj=None, data=None, request=None):
        if obj and obj.__class__ == Asset:
            # We don't have a subclass instance.  This is likely because
            # the object was retrieved through a RelatedField on another
            # resource
            obj = self._meta.queryset.get(asset_id=obj.asset_id)

        return super(AssetResource, self).build_bundle(obj, data, request)

    def obj_create(self, bundle, request=None, **kwargs):
        # Set the asset's owner to the request's user
        if request.user:
            kwargs['owner'] = request.user
        return super(AssetResource, self).obj_create(bundle, request, **kwargs)

    def apply_request_kwargs(self, obj_list, request=None, **kwargs):
        filters = {}
        story_id = kwargs.get('story_id')
        section_id = kwargs.get('section_id')
        no_section = kwargs.get('no_section')
        if story_id:
            filters['stories__story_id'] = story_id
        if section_id:
            filters['sectionasset__section__section_id'] = section_id

        new_obj_list = obj_list.filter(**filters)

        if no_section and story_id:
            new_obj_list = new_obj_list.exclude(sectionasset__section__story__story_id=story_id)

        return new_obj_list

    def dehydrate(self, bundle):
        # Exclude the filename field from the output
        del bundle.data['filename']
        return bundle
    
    def dehydrate_content(self, bundle):
        return bundle.obj.render(format="html")
