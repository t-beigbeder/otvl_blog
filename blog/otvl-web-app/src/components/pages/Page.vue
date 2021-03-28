<template>

  <div class="page-content p-2 w-full">

    <div class="py-2 max-w-5xl mx-auto">
      <h2>{{ content.heading }}</h2>
      <StreamField
        v-for="(stream_field, index) in streamFields"
        v-bind="stream_field"
        :position="index"
        :key="index"
        :meta="meta"
        :brand="content.brand"
      />
    </div>
  </div>

</template>

<script>
import ContainerMixin from './ContainerMixin.js'

export default {
  mixins: [ContainerMixin],

  name: 'Page'
}
</script>
