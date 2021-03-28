<template>

    <nav class="v-menu-bar">
      <div>
        <div class="flex">
          <div class="flex items-center">

            <div class="block md:hidden">
              <div class="v-menu-container">
                <a v-if="!touchMenuSeen" @click.stop="touchMenuState(true)" href="#">
                  <svg class="inline w-8 mx-1 my-1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M3 5a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 15a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd" />
                  </svg>
                </a>
                <a v-if="touchMenuSeen" @click.stop="touchMenuState(false)" href="#">
                  <svg class="inline w-8 mx-1 my-1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                  </svg>
                </a>
                <router-link to="/"><img class="ml-4 rounded-full py-1 h-12" src="/otvl-blog-brand.png"></router-link>
                <router-link class=v-menu-bar-item-link to="/">Blog</router-link>
              </div>
            </div>

            <div class="hidden md:block">
              <div class="v-menu-container">
                <router-link to="/"><img class="ml-4 rounded-full py-1" src="/otvl-blog-brand.png"></router-link>

                <MenuBarItem
                   v-for="item in this.menu" :key="item.label"
                   :to="item.targetUrl"
                   :subMenu="item.subMenu"
                >
                  {{ item.label }}
                </MenuBarItem>

              </div>
            </div>
          </div>
        </div>
      </div>
    </nav>

</template>

<script>
import MenuBarItem from './MenuBarItem.vue'

export default {
  name: 'MenuBar',

  components: {
    MenuBarItem
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
    touchMenuState(isOn) {
      this.$utils.fineDbgLog({MenuBar: this, touchMenuState: isOn})
      this.$emit('touchMenuState', isOn)
    }
  }
}
</script>
