<script>
import dataService from '@/components/dataService.js'
import ConfirmDialog from '@/components/dialogs/dialog-confirm.vue'

export default {
  name: 'dialog-delete-user',
  components: { ConfirmDialog },
  emits: ['refresh', 'exit'],
  data() {
    return {
      // loginStore: useLoginStore(),
      usersList: undefined
      // dialogModifyUserDetails: false,
      // editUser: undefined,
    }
  },
  mounted: function () {
    this.updateUsers()
  },
  methods: {
    updateUsers: function () {
      const self = this
      dataService.getUsers().then(function (data) {
        self.usersList = data.data
      })
    },
    async deleteUser(index) {
      if (
        await this.$refs.confirm.open('Confirm', 'Are you sure you want to delete this record?')
      ) {
        console.log(index)
      }
    }
  }
}
</script>

<template>
  <v-card prepend-icon="mdi-account-remove-outline" title="Delete User">
    <!-- The <ConfirmDialog> should be inserted inside the <v-card> otherwise
    the dialog works bad (for instance, do not add scrollbars) -->
    <ConfirmDialog ref="confirm"></ConfirmDialog>
    <v-progress-circular
      indeterminate
      class="mx-auto"
      v-if="usersList === undefined"
    ></v-progress-circular>
    <v-list lines="two" v-else>
      <v-list-subheader>Select users to delete</v-list-subheader>
      <v-list-item
        prepend-icon="mdi-account-circle-outline"
        v-for="user in usersList"
        :key="user.id"
        :title="user.username"
        :subtitle="user.email"
        @click="deleteUser(user.id)"
      >
        <template v-slot:append>
          <v-icon icon="mdi-delete-outline" />
        </template>
      </v-list-item>
    </v-list>
    <v-divider v-if="usersList !== undefined"></v-divider>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn text="Done" variant="tonal" @click="$emit('exit')"></v-btn>
    </v-card-actions>
  </v-card>
</template>

<style scoped></style>
