<template>
  <div class="home">
    {{ testkey }}<nest-select-key v-model="testkey"></nest-select-key>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import NestSelectKey from '../components/product/NestSelectKey.vue'

@Component({
  components: {
    NestSelectKey
  }

})
export default class Home extends Vue {
  private testkey = 'created'
}
</script>
