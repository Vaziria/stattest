<template>
  <select :value="value" @change="$emit('input', $event.target.value)">
    <option v-for="key in listKey" :key="key" :value="key">{{ key }}</option>
  </select>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

@Component({})
export default class SelectKey extends Vue {
  private listKey: string[] = [
    'created',
    'name',
    'price'
  ]

  @Prop() value: string
}

</script>
