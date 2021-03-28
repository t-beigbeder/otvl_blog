import axios from 'axios'
import { createApp, reactive } from 'vue'

import { utils, state } from 'otvl-web-lib'

import router from './router.js'
import apputils from './apputils.js'

import App from '../App.vue'

export const app = createApp(App)
app.config.globalProperties.$axios = axios
app.config.globalProperties.$utils = { ...utils, ...apputils }
app.config.globalProperties.$state = reactive(state)

app.use(router)

app.directive('click-outside', {

  beforeMount: function (el, binding) {
    el.clickOutsideEvent = function (event) {
      utils.fineDbgLog({el, event})
      if (!(el == event.target || el.contains(event.target))) {
        binding.value(event);
      }
    };
    document.body.addEventListener('click', el.clickOutsideEvent)
  },

  unmounted: function (el) {
    document.body.removeEventListener('click', el.clickOutsideEvent)
  }

});
