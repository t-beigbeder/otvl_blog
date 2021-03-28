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

      <p/>
      <template
        v-for="blog in publishedBlogs"
        :key="blog.name"
      >
        <hr class="mt-3"/>
        <div class="blog-list-box">
          <h6>{{ blog.meta.summary_heading }}</h6>
          <p class="blog-list-date">Published on {{ $utils.intlDate(blog.meta.publication_date) }}</p>
          <p class="blog-list-summary">{{ blog.meta.summary }}</p>
          <div class="blog-list-more">
            <AppLink
              :to="state.loadedXPath + '/' + blog.name"
            >
              Read more
            </AppLink>
          </div>
        </div>
      </template>

      <hr class="mt-3 lg:hidden"/>

    </div>

  </div>

  <div class="pl-2 lg:pl-4 pr-2 py-4 w-full max-w-xl lg:w-1/4">
    <div
      v-if="previewBlogs.length"
      class="blog-box mb-5 px-4 bg-gray-200"
    >
      <div class="text-red-800 text-center">Soon on this Blog</div>
      <hr class="my-1"/>
      <div class="blog-menu">
        <AppLink
          v-for="blog in previewBlogs"
          :key="blog.name"
          :to="state.loadedXPath + '/' + blog.name"
          class="blog-menu-line-soon"
        >
          {{ blog.meta.summary_heading }}
        </AppLink>
      </div>
    </div>
    <div class="blog-box px-4">
      <div class="text-center">Search articles...</div>
      <hr class="my-1"/>
      <div class="blog-menu">
        <AppLink
          :to="'' + state.loadedXPath"
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
import { IndexMixin } from 'otvl-web-lib'
import AppLink from '../navig/AppLink.vue'

export default {
  mixins: [ ContainerMixin, IndexMixin ],

  components: {
    AppLink
  },

  name: 'XBlog',

  computed: {
    publishedBlogs: function () {
      return this.index().filter(
        function (blog) {
          return (!('preview' in blog.meta) || !blog.meta.preview)
        }
      )
    },

    previewBlogs: function () {
      return this.index().filter(
        function (blog) {
          return (('preview' in blog.meta) && blog.meta.preview)
        }
      )
    }
  }

}
</script>
