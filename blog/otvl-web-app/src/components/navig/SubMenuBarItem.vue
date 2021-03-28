<template>

  <AppLink
    class="v-submenubar-item"
    v-bind="$attrs"
    @click="click"
    @mouseover="subMenuState(true, $event)"
    @mouseleave="subMenuState(false, $event)"
  >
    <slot />
  </AppLink>

</template>

<script>
import AppLink from './AppLink.vue'

export default {
  name: 'SubMenuBarItem',

  components: {
    AppLink
  },

  methods: {
    subMenuState(isOn, e) {
      this.$utils.fineDbgLog({SubMenuBarItem: this, e, 'type': e.type, isOn})
      this.$emit('subMenuState', {state: isOn, event: e})
    },
    click: function(e) {
      this.subMenuState(false, e)
    }
  }
}
</script>
