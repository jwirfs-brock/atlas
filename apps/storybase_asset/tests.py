from datetime import datetime
from django.template.defaultfilters import striptags, truncatewords
from django.test import TestCase
from models import (ExternalAsset, HtmlAsset, HtmlAssetTranslation,
    create_html_asset, create_external_asset)
from embedable_resource import EmbedableResource

class AssetModelTest(TestCase):
    def test_license_name(self):
        asset = HtmlAsset(license='CC BY')
        asset.save()
        translation = HtmlAssetTranslation(title="Test", asset=asset)
        translation.save()
        self.assertEqual(asset.license_name(), 'Attribution Creative Commons')

    def test_string_representation_from_title(self):
        """ Tests that the string representation of an Asset is the Asset's title """
        asset = HtmlAsset()
        asset.save()
        title = "Test Asset Title"
        translation = HtmlAssetTranslation(title=title, asset=asset)
        translation.save()
        self.assertEqual(unicode(asset), asset.title)

    def test_string_representation_from_asset_id(self):
        """ Tests that if a title is not specified, the string representation of the asset is based on the Asset ID """
        asset = HtmlAsset()
        asset.save()
        translation = HtmlAssetTranslation(asset=asset)
        translation.save()
        self.assertEqual(unicode(asset), "Asset %s" % asset.asset_id)

    def test_full_html_caption_nothing(self):
        """
        Test that full_html_caption() returns an empty string when there
        is no asset metadata to include in the caption
        """
        asset = create_html_asset(type='image', title='Test Asset')
        self.assertEqual(asset.full_caption_html(), '')

    def test_full_html_caption_caption_only(self):
        """
        Test that full_html_caption() includes the caption field text
        when there is only a caption to include in the caption
        """
        caption = "This is a test caption"
        asset = create_html_asset(type='image', title='Test Asset',
                                  caption=caption)
        self.assertIn(caption, asset.full_caption_html())

    def test_full_html_caption_attribution_only(self):
        """
        Test that full_html_caption() includes the attribution field text
        when there is only an attribution to include in the caption
        """
        attribution = "Some photographer"
        asset = create_html_asset(type='image', title='Test Asset',
                                  attribution=attribution)
        self.assertIn(attribution, asset.full_caption_html())

    def test_full_html_caption_attribution_caption(self):
        """
        Test that full_html_caption() includes both the caption and
        attribution field text when both are set 
        """
        attribution = "Some photographer"
        caption = "This is a test caption"
        asset = create_html_asset(type='image', title='Test Asset',
                                  attribution=attribution,
                                  caption=caption)
        self.assertIn(caption, asset.full_caption_html())
        self.assertIn(attribution, asset.full_caption_html())

    def dataset_html_nothing(self):
        """
        Test that dataset_html() returns nothing when there are no
        associated datasets
        """
        asset = create_html_asset(type='image', title='Test Asset')
        self.assertEqual(asset.dataset_html(), "")

    def dataset_html_one_dataset(self):
        """
        Test that dataset_html() lists a lone dataset associated
        with an Asset
        """
        asset = create_html_asset(type='image', title='Test Asset')
        self.fail("This tests needs to be implemented")

    def test_full_html_caption_dataset_only(self):
        """
        Test that full_html_caption() includes listed datasets
        when only datasets are associated with an asset
        """
        asset = create_html_asset(type='image', title='Test Asset')
        self.fail("This test needs to be implemented")


class HtmlAssetModelTest(TestCase):
    def test_string_representation_from_title(self):
        """ Tests that the string representation of an Html Asset is autogenerated from the Body field when no title is present """ 
        asset = HtmlAsset()
        asset.save()
        body = "Eboney Brown's kids range from age one to age nine, so it helps that her daycare center, Early Excellence, is just a short walk from Wyatt-Edison Charter School, where her older kids go. Early Excellence, which welcomes guests with a mural of a white Denver skyline set against a backdrop of blue mountains, serves families from as far away as Thornton and Green Valley Ranch. And many of those families, says Early Excellence director Jennifer Luke, are caught in a cycle of poverty and depend daily on regional transportation. \"I know they can't put a bus on every corner,\" says Luke, who knows many parents who combine public transportation with long walks - year round, no matter the weather."
        translation = HtmlAssetTranslation(body=body, asset=asset)
        translation.save()
        self.assertEqual(unicode(asset), truncatewords(striptags(asset.body), 4))

    def test_display_title_with_no_explicit_title(self):
        """ Tests that the display_title() method returns an automatically
        generated title when an explicit title isn't set

        """
        asset = HtmlAsset()
        asset.save()
        body = "Eboney Brown's kids range from age one to age nine, so it helps that her daycare center, Early Excellence, is just a short walk from Wyatt-Edison Charter School, where her older kids go. Early Excellence, which welcomes guests with a mural of a white Denver skyline set against a backdrop of blue mountains, serves families from as far away as Thornton and Green Valley Ranch. And many of those families, says Early Excellence director Jennifer Luke, are caught in a cycle of poverty and depend daily on regional transportation. \"I know they can't put a bus on every corner,\" says Luke, who knows many parents who combine public transportation with long walks - year round, no matter the weather."
        translation = HtmlAssetTranslation(body=body, asset=asset)
        translation.save()
        self.assertEqual(asset.display_title(),
                         truncatewords(striptags(asset.body), 4))

class EmbedableResourceTest(TestCase):
    def test_get_google_spreadsheet_embed(self):
        url = 'https://docs.google.com/spreadsheet/pub?key=0As2exFJJWyJqdDhBejVfN1RhdDg2b0QtYWR4X2FTZ3c&output=html' 
        expected = "<iframe width='500' height='300' frameborder='0' src='%s&widget=true'></iframe>" % url
        self.assertEqual(EmbedableResource.get_html(url), expected)

class AssetApiTest(TestCase):
    """ Test the public API for creating Assets """

    def test_create_html_asset(self):
        """ Test create_html_asset() """

        title = "Success Express"
        type = "quotation"
        attribution = "Ed Brennan, EdNews Colorado"
        source_url = "http://www.ednewsparent.org/teaching-learning/5534-denvers-success-express-rolls-out-of-the-station"
        asset_created = datetime.strptime('2011-06-03 00:00',
                                          '%Y-%m-%d %H:%M')
        status='published'
        body = """
        In both the Far Northeast and the Near Northeast, school buses 
        will no longer make a traditional series of stops in neighborhoods
        - once in the morning and once in the afternoon. Instead, a fleet
        of DPS buses will circulate between area schools, offering students
        up to three chances to catch the one that will get them to their
        school of choice on time.

        Martha Carranza, who has a child at Bruce Randolph, said that for
        students who have depended on RTD, "I was very worried because it
        is very dangerous for the children coming from Globeville and also
        from Swansea ... the kids were arriving late and sometimes missing
        classes altogether."

        And, said Carranza, "... we are very happy that with the new
        transportation system, no child will have any excuse to miss 
        school."
        """
        asset = create_html_asset(type, title, caption='', body=body,
            attribution=attribution, source_url=source_url, status=status,
            asset_created=asset_created)
        self.assertEqual(asset.title, title)
        self.assertEqual(asset.type, type)
        self.assertEqual(asset.attribution, attribution)
        self.assertEqual(asset.source_url, source_url)
        self.assertEqual(asset.asset_created, asset_created)
        self.assertEqual(asset.status, status)
        retrieved_asset = HtmlAsset.objects.get(pk=asset.pk)
        self.assertEqual(retrieved_asset.title, title)
        self.assertEqual(retrieved_asset.type, type)
        self.assertEqual(retrieved_asset.attribution, attribution)
        self.assertEqual(retrieved_asset.source_url, source_url)
        self.assertEqual(retrieved_asset.asset_created, asset_created)
        self.assertEqual(retrieved_asset.status, status)

    def test_create_external_asset(self):
        """ Test create_external_asset() """
        title = 'Large Flock of birds in pomona, CA'
        type = 'video'
        caption = 'An intense flock of birds outside a theater in Pomona, CA'
        asset_created = datetime.strptime('2007-04-11 00:00',
                                          '%Y-%m-%d %H:%M')
        url = 'http://www.youtube.com/watch?v=BJQycHkddhA'
        attribution = 'Geoffrey Hing'
        asset = create_external_asset(
            type,
            title,
            caption,
            url,
            asset_created=asset_created,
            attribution=attribution)
        self.assertEqual(asset.title, title)
        self.assertEqual(asset.type, type)
        self.assertEqual(asset.caption, caption)
        self.assertEqual(asset.asset_created, asset_created)
        self.assertEqual(asset.attribution, attribution)
        retrieved_asset = ExternalAsset.objects.get(pk=asset.pk)
        self.assertEqual(retrieved_asset.title, title)
        self.assertEqual(retrieved_asset.type, type)
        self.assertEqual(retrieved_asset.caption, caption)
        self.assertEqual(retrieved_asset.asset_created, asset_created)
        self.assertEqual(retrieved_asset.attribution, attribution)
