<script>
import { useVariablesStore } from '@/store.js'
import { defineAsyncComponent, markRaw } from 'vue'

const dialogComponents = import.meta.glob('./*.vue')

export default {
  name: 'dialog-generic',

  props: {
    value: Boolean,
    data: Object,
    componentFile: String
  },

  emits: ['refresh', 'update:modelValue'],

  computed: {
    showMe: {
      get() {
        return this.value
      },
      set(value) {
        this.$emit('update:modelValue', value)
      }
    }
  },

  mounted() {
    const loader = dialogComponents[this.componentFile]

    if (!loader) {
      console.error(
        `Dialog component not found: ${this.componentFile}`,
        Object.keys(dialogComponents)
      )
      return
    }

    this.myComponent = markRaw(
      defineAsyncComponent(loader)
    )
  },

  methods: {
    refresh(returnData) {
      this.showMe = false
      this.$emit('refresh', returnData)
    }
  },

  data() {
    return {
      variablesStore: useVariablesStore(),
      myComponent: undefined
    }
  }
}
</script>

<template>
  <v-dialog v-model="showMe" :max-width="variablesStore.dialogMaxWidth">
    <component
      v-if="myComponent !== undefined"
      :is="myComponent"
      v-bind="data"
      @refresh="refresh"
      @exit="showMe = false"
    />
  </v-dialog>
</template>

<style scoped></style>
