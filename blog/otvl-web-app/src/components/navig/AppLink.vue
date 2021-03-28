<template>
  <a v-if="isExternalLink" v-bind="$attrs" :href="to">
    <slot />
  </a>
  <router-link
    v-else-if="isInternalLink"
    v-bind="$props"
    custom
    v-slot="{ isActive, href, navigate }"
  >
    <a
      v-bind="$attrs"
      :href="href"
      @click="navigate($event), click($event)"
      :class="isActive ? activeClass: ''"
    >
      <slot />
    </a>
  </router-link>
  <a
    v-else
    v-bind="$attrs"
  >
    <slot />
  </a>

</template>

<script>
import { RouterLink } from 'vue-router'

export default {
  name: 'AppLink',

  props: {
    ...RouterLink.props
  },

  computed: {
    isExternalLink() {
      return typeof this.to === 'string' && this.to.startsWith('http')
    },
    isInternalLink() {
      return typeof this.to === 'string' && !this.to.startsWith('http') && this.to !== ''
    },
    hasNoLink() {
      return typeof this.to === 'string' && this.to === ''
    }
  },

  methods: {
    click: function(e) {
      this.$utils.fineDbgLog({AppLink: this, e})
    }
  }
}
</script>
