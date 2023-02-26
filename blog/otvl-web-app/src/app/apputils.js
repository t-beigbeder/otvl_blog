import { DateTime } from 'luxon'

const apputils = {

  configuration: {
    debug: false,
    fineDebug: false,
    apiServerUrl: 'http://otvl-dev-host:9090/api/v2',
    webServerUrl: 'http://otvl-dev-host:8080',
    defaultLocale: 'en',
    localRouteAnchorClicks: true
  },

  intlDate: function (isoDateStr, locale) {
    const dt = DateTime.fromISO(isoDateStr)
    const localLocale = locale ? locale : apputils.configuration.defaultLocale
    const res = dt.setLocale(localLocale).toLocaleString(DateTime.DATE_MED)
    return res
  },

  scrollStatus: null,

  scrollBehavior: function (to, from, savedPosition) {
    if (apputils.scrollStatus) {
      apputils.scrollStatus.savedPosition = savedPosition
    }
  },

  isTouchEnabledBck: function() {
    return false
  },
  isTouchEnabled: function() {
    return ( 'ontouchstart' in window ) ||
           ( navigator.maxTouchPoints > 0 ) ||
           ( navigator.msMaxTouchPoints > 0 );
  }

}

export default apputils
