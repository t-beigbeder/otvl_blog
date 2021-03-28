<template>

  <div class="page-content pl-2 pr-4 py-4 w-full lg:w-3/4">
    <div class="max-w-4xl mx-auto">

      <h2
        v-if="content.heading"
      >
        {{ content.heading }}
      </h2>

      <StreamField
        v-for="(stream_field, index) in streamFields"
        v-bind="stream_field"
        :position="index"
        :key="index"
        :meta="meta"
      />

      <hr class="mt-3 lg:hidden"/>

    </div>

  </div>

  <div class="pl-2 lg:pl-4 pr-2 py-4 w-full max-w-xl lg:w-1/4">
    <div class="blog-box px-4">
      <div class="text-center">Search articles...</div>
      <hr class="my-1"/>
      <div class="blog-menu">
        <AppLink
          :to="blogIndexPath()"
          class="blog-menu-line"
        >
          List of articles
        </AppLink>
        <span class="blog-menu-line-disallowed">Other search criteria...</span>
      </div>
    </div>
  </div>

</template>

<script>
import ContainerMixin from './ContainerMixin.js'
import AppLink from '../navig/AppLink.vue'

export default {
  mixins: [ContainerMixin],

  components: {
    AppLink
  },

  name: 'Blog',

  methods: {
    blogIndexPath: function() {
      return "/blog"
    }
  }

}
</script>
