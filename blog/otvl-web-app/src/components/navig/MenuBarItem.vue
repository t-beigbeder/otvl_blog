<template>
  <div class=v-menu-bar-item>
    <AppLink
      v-if="to !== ''"
      class=v-menu-bar-item-link
      v-bind="$attrs"
      :to="to"
      @click="click"
      @mouseover="subMenuState(true, $event)"
      @mouseleave="subMenuState(false, $event)"
    >
      <slot />
      <svg
        v-if="subMenu.length"
        class="inline w-5"
        xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
      </svg>

    </AppLink>
    <div
      v-else
      class=v-menu-bar-item-link
      @click="click"
      @mouseover="subMenuState(true, $event)"
      @mouseleave="subMenuState(false, $event)"
    >
      <slot />
      <svg
        v-if="subMenu.length"
        class="inline w-5"
        xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
      </svg>
    </div>
    <div
      v-show="isSubMenuDisplayed"
      class="v-menu-bar-dropdown"
    >
      <SubMenuBarItem v-for="item in subMenu" :key="item.label"
        class="desk-submenu"
        :to="item.targetUrl"
        @sub-menu-state="subMenuStateEvent"
      >
        {{ item.label }}
      </SubMenuBarItem>
    </div>
  </div>

</template>

<script>
import AppLink from './AppLink.vue'
import SubMenuBarItem from './SubMenuBarItem.vue'

export default {
  name: 'MenuBarItem',

  components: {
    AppLink,
    SubMenuBarItem
  },

  props: {
    to: {
      type: String,
      default: ''
    },
    subMenu: {
      type: Array,
      default: function () {
        return []
      }
    }
  },

  data: function () {
    return {
      isSubMenuDisplayed: false
    }
  },

  methods: {
    subMenuState(isOn, e, fromSubMenu) {
      if ( e.type === 'mouseover' && this.$utils.isTouchEnabled() && !fromSubMenu) {
        return
      }
      if (this.subMenu.length) {
        this.isSubMenuDisplayed = isOn
      }
      this.$utils.fineDbgLog({MenuBarItem: this, e, fromSubMenu, 'type': e.type, isSubMenuDisplayed: this.isSubMenuDisplayed})
    },
    click(e) {
      this.subMenuState(!this.isSubMenuDisplayed, e)
    },
    subMenuStateEvent(data) {
      this.$utils.fineDbgLog({MenuBarItemEvent: this, data, isSubMenuDisplayed: this.isSubMenuDisplayed})
      this.subMenuState(data.state, data.event, true)
    }
  }
}
</script>
