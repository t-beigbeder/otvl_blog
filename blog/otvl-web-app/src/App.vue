<template>

  <div class="app-style">

    <MenuBar
      :menu="menu"
      :touch-menu-seen="touchMenuSeen"
      @touch-menu-state="touchMenuStateEvent"
    />

    <TouchMenu
      :menu="menu"
      :touch-menu-seen="touchMenuSeen"
      @click-outside-nav="clickOutsideNavEvent"
      @click-nav="clickNavEvent"
    />

    <div class="lg:mx-12 md:mx-8 mx-auto flex flex-wrap">

      <router-view/>

      <hr class="border-gray-500 mt-4 md:mt-8 lg:mt-12 w-full"/>
      <div class="page-footer mt-2 mx-auto">
        <router-link to="/about">About</router-link>
        <span class="mx-2"><b>·</b></span>
        <router-link to="/about/legal-policies">Legal Policies</router-link>
      </div>
    </div>

  </div>

</template>

<script>
import { AppMixin, otvlWebLibId } from 'otvl-web-lib'
import MenuBar from './components/navig/MenuBar.vue'
import TouchMenu from './components/navig/TouchMenu.vue'
import menu from './app/menu.js'
import apputils from './app/apputils.js'

export default {
  mixins: [AppMixin],

  name: 'App',

  components: {
    MenuBar,
    TouchMenu
  },

  data: function () {
    return {
      menu,
      touchMenuSeen: false
    }
  },

  created: function () {
    this.getStaticConfiguration()
    this.$utils.dbgLog({'App created': this, otvlWebLibId})
    this.$utils.fineDbgLog( { 'isTouchEnabled': this.$utils.isTouchEnabled() } )
    this.fetchConfiguration()
    apputils.scrollStatus = this.$state.scrollStatus
  },

  methods: {
    getStaticConfiguration: function() {
      var dApp = document.getElementById('app')
      var apiServerUrl = dApp.getAttribute('api-server-url')
      if (apiServerUrl !== 'default_api_server_url') {
        apputils.configuration.apiServerUrl = apiServerUrl
      }
      var webServerUrl = dApp.getAttribute('web-server-url')
      if (webServerUrl !== 'default_web_server_url') {
        apputils.configuration.webServerUrl = webServerUrl
      }
    },

    touchMenuStateEvent(state) {
      this.touchMenuSeen = state
      this.$utils.fineDbgLog({App: this, touchMenuSeen: this.touchMenuSeen})
    },

    clickOutsideNavEvent() {
      this.$utils.fineDbgLog({clickOutsideNavEvent: this})
      this.touchMenuStateEvent(false)
    },

    clickNavEvent() {
      this.$utils.fineDbgLog({clickNavEvent: this})
      this.touchMenuStateEvent(false)
    }
  }
}
</script>
