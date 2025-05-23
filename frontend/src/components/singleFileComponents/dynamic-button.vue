<script>
export default {
  props: {
    text: String,
    icon: String,
    color: {
      type: String,
      default: 'primary'
    }
  },
  computed: {
    isIcon() {
      return !!this.$vuetify.display.mdAndDown
    }
  }
}
</script>

<template>
  <v-btn v-if="isIcon" :color="color" variant="elevated" :icon="this.icon">
    <v-icon></v-icon>
    <v-tooltip activator="parent" location="top">{{ text }} </v-tooltip>
  </v-btn>
  <v-btn v-else :color="color" variant="elevated" :prepend-icon="this.icon" :text="this.text" />
</template>
