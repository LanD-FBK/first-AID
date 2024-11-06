<script>
import { useVariablesStore } from '@/store.js'
import { defineAsyncComponent, getCurrentInstance, markRaw } from 'vue'

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
    this.myComponent = markRaw(
      defineAsyncComponent(() =>
        import(this.componentFile).then().catch(() => {
          // ignored
        })
      )
    )
  },
  methods: {
    refresh: function () {
      this.showMe = false
      if (getCurrentInstance()?.vnode?.props?.refresh) {
        this.$emit('refresh')
      }
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
