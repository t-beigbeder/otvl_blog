<template>

  <div class="page-content px-2 w-full">

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
import { IndexMixin } from 'otvl-web-lib'

export default {

  mixins: [ ContainerMixin, IndexMixin ],

  name: 'XPage',

}
</script>
