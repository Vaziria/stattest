<template>
  <select-key></select-key>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import SelectKey from './SelectKey.vue'

interface Test {}

@Component({
  components: {
    SelectKey
  }
})
export default class NestSelectKey extends Vue {
  private listKey: string[] = [
    'created',
    'name',
    'price'
  ]

  @Prop() value: string
}

</script>
