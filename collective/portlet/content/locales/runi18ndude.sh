#!/bin/sh

DOMAIN='collective.portlet.content'

i18ndude rebuild-pot --pot ./${DOMAIN}.pot --create ${DOMAIN} ..

i18ndude sync --pot ./${DOMAIN}.pot ./*/LC_MESSAGES/${DOMAIN}.po


i18ndude sync --pot ./plone.pot ./*/LC_MESSAGES/plone.po