<script>
import dataService from './components/dataService'
import SnackbarGeneric from './components/singleFileComponents/snackbar-generic.vue'
import { useLoginStore, useVariablesStore } from './store'
import DialogGeneric from '@/components/dialogs/dialog-generic.vue'

export default {
  components: { DialogGeneric, SnackbarGeneric },
  data() {
    return {
      ds: dataService,
      loginStore: useLoginStore(),
      variablesStore: useVariablesStore(),

      //Create project dialog vars
      dialogCreateProject: false,
      dialogCreateUser: false,
      dialogEditUser: false,
      dialogDeleteUser: false,

      loadingCreateProject: false,
      isProjectAdmin: false,

      //Error handling vars
      // errorDialog: false,
      // errorUserDialogText: '',

      showSnackbar: false,
      snackbarMessage: ''
    }
  },
  watch: {
    // dialogCreateUser(newValue, oldValue) {
    //   //If dialog is closed, clears all fields
    //   if (newValue == false && oldValue == true) {
    //     this.newUserUsername = ''
    //     this.newUserEmail = ''
    //     this.newUserPassword = ''
    //     this.newUserPasswordCheck = ''
    //     this.isNewUserPasswordError = false
    //     this.newUserPasswordErrorMessage = ''
    //   }
    // },
    // editUserIsActive(newValue, oldValue) {
    //   const self = this
    //   console.log('isactive changed. New value: ' + newValue)
    //   if (oldValue != undefined && newValue != undefined) {
    //     this.editUserIsActiveLoading = true
    //     console.log('isactive changed. New value: ' + newValue)
    //     dataService.changeActiveState(this.editUserID).then(function (data) {
    //       console.log('changed.')
    //       console.log(data)
    //       self.editUserIsActiveLoading = false
    //     })
    //   }
    // },
    // dialogModifyUserDetails(newValue, oldValue) {
    //   if (newValue === false && oldValue === true) {
    //     this.editUserUsername = ''
    //     this.editUserEmail = ''
    //     this.editUserPassword = ''
    //     this.editUSerPasswordCheck = ''
    //     //Triggers usersList watcher in order to refresh the variable
    //     this.usersList = undefined
    //     this.editUserIsActive = undefined
    //   }
    // },
    //Refreshes the variable everytime users' details get changed
    //Everytime the variable need a refresh it gets set to 'undefined'
    //Eager watcher so it fetches the list on page load
    // usersList(newValue, oldValue) {
    //   const self = this
    //   if (newValue == undefined) {
    //     dataService.getUsers().then(function (data) {
    //       self.usersList = data.data
    //     })
    //   }
    // }
  },
  methods: {
    //Warning: Not atomic, try to move in 'snackbar-generic.vue'
    successSnackbar: function (callingDialog) {
      //TODO: change how message picking works. This is too convoluted and resource heavy
      if (callingDialog == 'createUser') {
        this.snackbarMessage = 'New User Created Successfully'
      }
      this.showSnackbar = true
    },
    changeBearer: function () {
      /*
      Just making the call to '/users/me' is enough to update the Bearer
      token as the Response interceptor in 'axios.js' changes the token everytime a successful
      API call is made
      */
      dataService.returnToken()
    },
    goToPrevious: function () {
      //TODO: complete with all annotation routes
      const route = this.$route.name
      if (route == 'tasks') return this.$router.push({ name: 'projects' })
      else if (route == 'annotation' || 'annotation_edit')
        return this.$router.push({ name: 'tasks' })
    }
  },
  mounted: function () {
    //The function call is not written directly in setInterval due to security concerns:
    //https://developer.mozilla.org/en-US/docs/Web/API/Window/setInterval
    setInterval(() => {
      this.changeBearer()
    }, this.variablesStore.apiPingInterval)
  }
}
</script>

<template>
  <v-app>
    <v-app-bar color="primary">
      <v-app-bar-nav-icon icon="mdi-abacus" @click="this.$router.push({ name: 'projects' })" />
      <v-app-bar-nav-icon icon="mdi-arrow-u-left-top" @click="this.goToPrevious()" />
      <v-toolbar-title>Annotation Interface</v-toolbar-title>
      <v-menu v-if="loginStore.is_admin">
        <template v-slot:activator="{ props }">
          <v-btn v-bind="props">Manage Users</v-btn>
        </template>
        <v-list>
          <v-list-item prepend-icon="mdi-account-plus-outline" @click="dialogCreateUser = true"
            >New User
          </v-list-item>
          <v-list-item prepend-icon="mdi-account-edit-outline" @click="dialogEditUser = true"
            >Edit User
          </v-list-item>
          <v-list-item prepend-icon="mdi-account-remove-outline" @click="dialogDeleteUser = true"
            >Delete User
          </v-list-item>
        </v-list>
      </v-menu>

      <v-menu v-if="loginStore.isToken()">
        <template v-slot:activator="{ props }">
          <v-btn prepend-icon="mdi-account-circle-outline" v-bind="props"
            >{{ loginStore.username }}
          </v-btn>
        </template>
        <v-list>
          <v-list-item @click="this.$router.push({ name: 'changePassword' })"
            >Change Password
          </v-list-item>
          <v-list-item @click="ds.logout()">Logout</v-list-item>
        </v-list>
      </v-menu>
    </v-app-bar>
    <v-main>
      <DialogGeneric
        v-if="loginStore.is_admin"
        v-model="dialogCreateUser"
        component-file="./dialog-create-user.vue"
        @refresh="this.successSnackbar('createUser')"
      ></DialogGeneric>
      <DialogGeneric
        v-if="loginStore.is_admin"
        v-model="dialogEditUser"
        component-file="./dialog-edit-user.vue"
      ></DialogGeneric>
      <DialogGeneric
        v-if="loginStore.is_admin"
        v-model="dialogDeleteUser"
        component-file="./dialog-delete-user.vue"
      ></DialogGeneric>

      <!--      <v-dialog v-model="errorDialog" :max-width="variablesStore.errorMaxWidth">-->
      <!--        <v-card-->
      <!--          title="Error!"-->
      <!--          prepend-icon="mdi-alert-circle"-->
      <!--          color="error"-->
      <!--          :text="errorUserDialogText + '. Please try again.'"-->
      <!--        >-->
      <!--          <v-card-actions>-->
      <!--            <v-btn @click="errorDialog = false" text="Close"></v-btn>-->
      <!--          </v-card-actions>-->
      <!--        </v-card>-->
      <!--      </v-dialog>-->

      <!--      <v-snackbar v-model="successNewUserSnackbar" timeout="2000"-->
      <!--        >New User created successfully!-->
      <!--        <template v-slot:actions>-->
      <!--          <v-btn color="blue" variant="text" @click="successNewUserSnackbar = false"> Close </v-btn>-->
      <!--        </template>-->
      <!--      </v-snackbar>-->

      <!--      <v-dialog v-model="dialogWarnDeleteUser" :max-width="variablesStore.errorMaxWidth">-->
      <!--        <v-card-->
      <!--          color="warning"-->
      <!--          prepend-icon="mdi-alert"-->
      <!--          title="Are you sure?"-->
      <!--          :text="-->
      <!--            'Do you really want to delete user ' +-->
      <!--            deletingUserName +-->
      <!--            '? This action cannot be undone'-->
      <!--          "-->
      <!--        >-->
      <!--          <v-card-actions>-->
      <!--            <v-spacer></v-spacer>-->
      <!--            <v-btn text="Back" @click="dialogWarnDeleteUser = false"></v-btn>-->
      <!--            <v-btn text="Delete" variant="tonal" @click="confirmDeleteUser(deletingUserID)"></v-btn>-->
      <!--          </v-card-actions>-->
      <!--        </v-card>-->
      <!--      </v-dialog>-->

      <SnackbarGeneric
        v-model="showSnackbar"
        :message="this.snackbarMessage"
        @close="this.showSnackbar = false"
      />
      <router-view :key="$route.path"></router-view>
    </v-main>
  </v-app>
</template>
