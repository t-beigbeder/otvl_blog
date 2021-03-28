<template>

    <nav
      v-show="touchMenuSeen"
      v-click-outside="clickOutsideNav"
      @click="click"
      class="v-touch-menu-container block md:hidden"
    >

      <template
        v-for="item in this.menu" :key="item.label"
      >
        <AppLink
          :to="item.targetUrl"
          class="v-touch-menu-item"
        >
          {{ item.label }}
        </AppLink>

        <AppLink
          v-for="subItem in item.subMenu" :key="subItem.label"
          :to="subItem.targetUrl"
          class="v-touch-submenu-item"
        >
          {{ subItem.label }}
        </AppLink>
      </template>
    </nav>

</template>

<script>
import AppLink from './AppLink.vue'

export default {
  name: 'TouchMenu',

  components: {
    AppLink
  },

  props: {
    menu: {
      type: Array
    },
    touchMenuSeen: {
      type: Boolean
    }
  },

  methods: {
    clickOutsideNav() {
      this.$utils.fineDbgLog({clickOutsideNav: this})
      this.$emit('clickOutsideNav')
    },
    click: function(e) {
      this.$utils.fineDbgLog({TouchMenu: this, e})
      this.$emit('clickNav')
    }

  }
}
</script>
