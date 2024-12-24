<script>
export default {
  data() {
    return {
      //Placeholder
    }
  },
  props: {
    message: String
  },
  emits: ['close']
}
</script>

<template>
  <v-snackbar timeout="2000"
    >{{ this.message }}
    <template v-slot:actions>
      <v-btn color="blue" variant="text" @click="this.$emit('close')"> Close </v-btn>
    </template>
  </v-snackbar>
</template>
