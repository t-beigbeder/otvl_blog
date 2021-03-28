import { PageMixin } from 'otvl-web-lib'
import StreamField from '../content/StreamField.vue'

export default {

  mixins: [PageMixin],

  components: {
    StreamField
  },

  watch: {
    loadedStreamFields() {
      this.$utils.fineDbgLog({'ContainerMixin loadedStreamFields': this})
      for ( let lsf of this.loadedStreamFields ) {
        this.streamFields.push(lsf)
      }
    }
  }

}
