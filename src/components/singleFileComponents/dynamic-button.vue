<script>
export default {
  props: {
    text: String,
    icon: String
  },
  computed: {
    isIcon() {
      return this.$vuetify.display.mdAndDown ? true : false
    },
    isDeleteColor() {
      return this.text == 'Delete' ? 'error' : 'primary'
    }
  }
}
</script>

<template>
  <v-btn v-if="isIcon" :color="isDeleteColor" variant="elevated" :icon="this.icon" />
  <v-btn
    v-else
    :color="isDeleteColor"
    variant="elevated"
    :prepend-icon="this.icon"
    :text="this.text"
  />
</template>
