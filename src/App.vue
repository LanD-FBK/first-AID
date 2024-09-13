<script>
import dataService from './components/dataService'
import { useLoginStore, useVariablesStore } from './store'

export default {
  data() {
    return {
      ds: dataService,
      loginStore: useLoginStore(),
      variablesStore: useVariablesStore(),
      usersList: undefined,

      //Create project dialog vars
      dialogCreateProject: false,
      loadingCreateProject: false,
      projectName: '',
      isProjectActive: false,
      projectUsersList: [],
      adminUsersList: [],
      rulesCreateProject: [
        function (value) {
          if (value) return true
          return 'Please provide a project name'
        }
      ],
      validNewProjectData: false,
      successNewProjectSnackbar: false,
      isProjectAdmin: false,

      //Create user dialog vars
      dialogCreateUser: false,
      validNewUserData: false,
      rulesCreateUser: [
        function (value) {
          if (value) return true
          return 'This field cannot be empty'
        }
      ],
      newUserUsername: '',
      newUserEmail: '',
      newUserPassword: '',
      newUserPasswordCheck: '',
      showNewUserPassword: false,
      showNewUserPasswordCheck: false,
      loadingCreateUser: false,
      //Vars to 'error' password fields
      isNewUserPasswordError: false,
      newUserPasswordErrorMessage: '',
      //Snackbar vars
      successNewUserSnackbar: false,

      //Error handling vars
      errorDialog: false,
      errorUserDialogText: '',

      //Edit user dialog vars
      dialogEditUser: false,
      dialogModifyUserDetails: false,
      validEditUserData: false,
      editUserID: undefined,
      editUserUsername: '',
      editUserEmail: '',

      //Is user's password being changed?
      isEditUserPasswordChange: false,
      editUserPassword: '',
      editUSerPasswordCheck: '',
      showEditUserPassword: false,
      showEditUserPasswordCheck: false,
      isEditUserPasswordError: false,
      editPasswordErrorMessage: '',
      editUserIsActive: undefined,
      editUserIsActiveLoading: false,
      isUserModifyDialogLoaded: false,
      loadingModifyUserDetails: false,

      //Delete user dialog vars
      dialogDeleteUser: false,
      dialogWarnDeleteUser: false,
      deletingUserName: undefined,
      deletingUserID: undefined,
      confirmDeleteUserLoading: false
    }
  },
  methods: {
    //New project creation funcs
    submitNewProject: function () {
      const self = this
      if (this.validNewProjectData) {
        this.loadingCreateProject = true
        //Works but extremely convoluted

        //In order to avoid JS' shallow copy
        let submitAdminList = Array.from(this.projectUsersList)

        for (let user of submitAdminList) {
          if (this.adminUsersList.includes(user))
            //This is because we don't know if positions within the two arrays are the same
            submitAdminList[submitAdminList.indexOf(user)] = true
          else submitAdminList[submitAdminList.indexOf(user)] = false
        }
        dataService
          .createProject(
            this.projectName,
            this.isProjectActive,
            this.projectUsersList,
            submitAdminList
          )
          .then(function (data) {
            //Can't be seen as router immediately changes page
            self.successNewProjectSnackbar = true
            self.$router.go(0)
            //Maybe create a prop to force a component update instead of a page update?
            //This way the snackbar can be seen
          })
          .catch(function (error) {
            self.errorDialog = true
            self.errorUserDialogText = error.message
          })
      }
    },
    isProjectAdminDisplay: function (userID) {
      return this.adminUsersList.includes(userID) ? 'Admin User' : 'Normal User'
    },
    isAdminButtonDisabled: function (userID) {
      return this.projectUsersList.includes(userID) ? false : true
    },

    //New user creation funcs
    submitNewUser: function () {
      const self = this
      if (this.validNewUserData) {
        this.loadingCreateUser = true
        //Checks if passwords match
        if (this.newUserPassword === this.newUserPasswordCheck) {
          console.log('match')
          dataService
            .createUser(this.newUserEmail, this.newUserUsername, this.newUserPassword)
            .then(function (data) {
              self.usersList = undefined
              self.loadingCreateUser = false
              self.dialogCreateUser = false
              self.successNewUserSnackbar = true
            })
            .catch(function (error) {
              self.errorDialog = true
              self.errorUserDialogText = error.message
              self.loadingCreateUser = false
              //Also clear all fields? Maybe watch() can be used?
            })
        } else {
          this.isNewUserPasswordError = true
          this.newUserPasswordErrorMessage = 'Passwords do not match!'
          this.loadingCreateUser = false
        }
      }
    },
    //User edit funcs
    openUserModifyDialog: function (username, email, isActive, userID) {
      this.editUserID = userID
      this.dialogModifyUserDetails = true
      this.editUserUsername = username
      this.editUserEmail = email
      this.editUserIsActive = Boolean(isActive)
      this.isUserModifyDialogLoaded = true
    },
    submitEditUser: function () {
      const self = this
      if (this.validEditUserData) {
        this.loadingModifyUserDetails = true
        if (this.editUserPassword === this.editUSerPasswordCheck) {
          dataService
            .editUser(
              this.editUserEmail,
              this.editUserUsername,
              this.editUSerPassword,
              this.editUserID
            )
            .then(function (data) {
              console.log(data)
              self.loadingModifyUserDetails = false
              self.dialogModifyUserDetails = false
            })
            .catch(function (error) {
              self.errorDialog = true
              self.errorUserDialogText = error.message
              console.log(error)
            })
        } else {
          this.isEditUserPasswordError = true
          this.editPasswordErrorMessage = 'Passwords do not match!'
        }
      }
    },
    //User deletion funcs
    openDeleteEditUserDialog: function (dialogType) {
      if (dialogType == 'delete') this.dialogDeleteUser = true
      else this.dialogEditUser = true
    },
    openWarningDeleteDialog: function (deletingUserID, deletingUserName) {
      this.dialogWarnDeleteUser = true
      this.deletingUserID = deletingUserID
      this.deletingUserName = deletingUserName
    },
    confirmDeleteUser: function () {
      this.confirmDeleteUserLoading = true
      const self = this
      dataService
        .deleteUser(this.deletingUserID)
        .then(function (data) {
          console.log(data)
          self.deletingUserID = undefined
          self.deletingUserName = undefined
          self.usersList = undefined
          self.openDeleteEditUserDialog('delete')
          self.confirmDeleteUserLoading = false
          self.dialogWarnDeleteUser = false
        })
        .catch(function (error) {
          self.errorDialog = true
          self.errorUserDialogText = error.message
        })
    }
  },
  computed: {
    isProjectsList() {
      return this.$route.name == 'projects' ? true : false
    },
    isAdmin() {
      return this.loginStore.username == 'admin' ? true : false
    }
  },
  watch: {
    dialogCreateUser(newValue, oldValue) {
      //If dialog is closed, clears all fields
      if (newValue == false && oldValue == true) {
        this.newUserUsername = ''
        this.newUserEmail = ''
        this.newUserPassword = ''
        this.newUserPasswordCheck = ''
        this.isNewUserPasswordError = false
        this.newUserPasswordErrorMessage = ''
      }
    },
    editUserIsActive(newValue, oldValue) {
      const self = this
      console.log('isactive changed. New value: ' + newValue)
      if (oldValue != undefined && newValue != undefined) {
        this.editUserIsActiveLoading = true
        console.log('isactive changed. New value: ' + newValue)
        dataService.changeActiveState(this.editUserID).then(function (data) {
          console.log('changed.')
          console.log(data)
          self.editUserIsActiveLoading = false
        })
      }
    },
    dialogModifyUserDetails(newValue, oldValue) {
      if (newValue === false && oldValue === true) {
        this.editUserUsername = ''
        this.editUserEmail = ''
        this.editUserPassword = ''
        this.editUSerPasswordCheck = ''
        //Triggers usersList watcher in order to refresh the variable
        this.usersList = undefined
        this.editUserIsActive = undefined
      }
    },

    //Refreshes the variable everytime users' details get changed
    //Everytime the variable need a refresh it gets set to 'undefined'
    //Eager watcher so it fetches the list on page load
    usersList: {
      handler(newValue, oldValue) {
        const self = this
        if (newValue == undefined) {
          dataService.getUsers().then(function (data) {
            self.usersList = data.data
          })
        }
      },
      immediate: true
    }

    /*
    usersList(newValue, oldValue) {
      console.log('userslist watcher')
      const self = this
      if (newValue == undefined) {
        dataService.getUsers().then(function (data) {
          self.usersList = data.data
        })
      }
    }
      */
  }
}
</script>

<template>
  <v-app>
    <v-app-bar color="primary">
      <v-app-bar-nav-icon
        icon="mdi-abacus"
        @click="this.$router.push({ name: 'projects' })"
      ></v-app-bar-nav-icon>
      <v-toolbar-title>Annotation Interface</v-toolbar-title>
      <v-menu v-if="isAdmin">
        <template v-slot:activator="{ props }">
          <v-btn v-bind="props">Manage Users</v-btn>
        </template>
        <v-list>
          <v-list-item prepend-icon="mdi-account-plus-outline" @click="dialogCreateUser = true"
            >New User</v-list-item
          >
          <v-list-item
            prepend-icon="mdi-account-edit-outline"
            @click="openDeleteEditUserDialog('edit')"
            >Edit User</v-list-item
          >
          <v-list-item
            prepend-icon="mdi-account-remove-outline"
            @click="openDeleteEditUserDialog('delete')"
            >Delete User</v-list-item
          >
        </v-list>
      </v-menu>

      <v-menu v-if="loginStore.isToken()">
        <template v-slot:activator="{ props }">
          <v-btn prepend-icon="mdi-account-circle-outline" v-bind="props">{{
            loginStore.username
          }}</v-btn>
        </template>
        <v-list>
          <v-list-item @click="this.$router.push({ name: 'changePassword' })"
            >Change Password</v-list-item
          >
          <v-list-item @click="ds.logout()">Logout</v-list-item>
        </v-list>
      </v-menu>
    </v-app-bar>
    <v-main>
      <!--Create User dialog-->
      <v-dialog v-model="dialogCreateUser" :max-width="variablesStore.dialogMaxWidth">
        <v-card prepend-icon="mdi-account-plus-outline" title="Create New User">
          <v-form
            v-model="validNewUserData"
            :rules="rulesCreateUser"
            @submit.prevent="submitNewUser"
          >
            <v-card-text>
              <v-text-field
                label="Username"
                required
                v-model="newUserUsername"
                :rules="rulesCreateUser"
              />
              <v-text-field
                label="Email"
                required
                v-model="newUserEmail"
                :rules="rulesCreateUser"
                type="email"
              />
              <v-text-field
                label="Password"
                required
                v-model="newUserPassword"
                :rules="rulesCreateUser"
                :type="showNewUserPassword ? 'text' : 'password'"
                :append-icon="showNewUserPassword ? 'mdi-eye' : 'mdi-eye-off'"
                @click:append="showNewUserPassword = !showNewUserPassword"
                :error="isNewUserPasswordError"
                :error-messages="newUserPasswordErrorMessage"
              />
              <v-text-field
                label="Password check"
                required
                v-model="newUserPasswordCheck"
                :rules="rulesCreateUser"
                :type="showNewUserPasswordCheck ? 'text' : 'password'"
                :append-icon="showNewUserPasswordCheck ? 'mdi-eye' : 'mdi-eye-off'"
                @click:append="showNewUserPasswordCheck = !showNewUserPasswordCheck"
                :error="isNewUserPasswordError"
                :error-messages="newUserPasswordErrorMessage"
              />
            </v-card-text>
            <v-divider></v-divider>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn @click="dialogCreateUser = false" text="Cancel" />
              <v-btn
                color="primary"
                variant="tonal"
                :loading="loadingCreateUser"
                type="submit"
                text="Create"
              />
            </v-card-actions>
          </v-form>
        </v-card>
      </v-dialog>

      <v-dialog v-model="errorDialog" :max-width="variablesStore.errorMaxWidth">
        <v-card
          title="Error!"
          prepend-icon="mdi-alert-circle"
          color="error"
          :text="errorUserDialogText + '. Please try again.'"
        >
          <v-card-actions>
            <v-btn @click="errorDialog = false" text="Close"></v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <v-snackbar v-model="successNewUserSnackbar" timeout="2000"
        >New User created successfully!
        <template v-slot:actions>
          <v-btn color="blue" variant="text" @click="snackbar = false"> Close </v-btn>
        </template>
      </v-snackbar>

      <!--Edit user dialog-->
      <v-dialog v-model="dialogEditUser" :max-width="variablesStore.dialogMaxWidth">
        <v-card prepend-icon="mdi-account-edit-outline" title="Edit User">
          <v-progress-circular
            indeterminate
            class="mx-auto"
            v-if="usersList == undefined"
          ></v-progress-circular>
          <v-list lines="two" v-else>
            <v-list-subheader>Select the User to edit</v-list-subheader>
            <v-list-item
              prepend-icon="mdi-account-circle-outline"
              v-for="user in usersList"
              :key="user.id"
              :title="user.username"
              :subtitle="user.email"
              @click="openUserModifyDialog(user.username, user.email, user.is_active, user.id)"
            >
              <template v-slot:append>
                <v-icon icon="mdi-pencil" />
              </template>
            </v-list-item>
          </v-list>
          <v-divider v-if="usersList != undefined"></v-divider>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn text="Done" variant="tonal" @click="dialogEditUser = false"></v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <v-dialog v-model="dialogModifyUserDetails" :max-width="variablesStore.dialogMaxWidth">
        <v-card title="Edit User" prepend-icon="mdi-account-edit-outline">
          <v-form
            @submit.prevent="submitEditUser"
            v-model="validEditUserData"
            :ruiles="rulesCreateUser"
          >
            <v-card-text>
              <v-row dense>
                <v-col cols="12" md="9" sm="9">
                  <v-text-field
                    label="Username"
                    type="text"
                    v-model="editUserUsername"
                    :rules="rulesCreateUser"
                  ></v-text-field>
                </v-col>
                <v-col cols="12" md="3" sm="3">
                  <v-checkbox
                    label="Is Active"
                    class="ml-2"
                    v-model="editUserIsActive"
                    :undefined="editUserIsActiveLoading ? true : false"
                    :disabled="editUserIsActiveLoading ? true : false"
                  ></v-checkbox>
                </v-col>
                <v-col cols="12">
                  <v-text-field label="Email" type="email" v-model="editUserEmail"></v-text-field>
                  <v-text-field
                    label="Password"
                    :type="showEditUserPassword ? 'text' : 'password'"
                    :append-icon="showEditUserPassword ? 'mdi-eye' : 'mdi-eye-off'"
                    @click:append="showEditUserPassword = !showEditUserPassword"
                    v-model="editUserPassword"
                    :error="isEditUserPasswordError"
                    :error-messages="editPasswordErrorMessage"
                  ></v-text-field>
                  <v-text-field
                    label="Password Check"
                    :type="showEditUserPasswordCheck ? 'text' : 'password'"
                    :append-icon="showEditUserPassword ? 'mdi-eye' : 'mdi-eye-off'"
                    @click:append="showEditUserPassword = !showEditUserPassword"
                    v-model="editUSerPasswordCheck"
                    :error="isEditUserPasswordError"
                    :error-messages="editPasswordErrorMessage"
                  ></v-text-field>
                </v-col>
              </v-row>
            </v-card-text>
            <v-divider></v-divider>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn @click="dialogModifyUserDetails = false" text="Back" />
              <v-btn
                color="primary"
                variant="tonal"
                :loading="loadingModifyUserDetails"
                type="submit"
                text="Confirm"
              />
            </v-card-actions>
          </v-form>
        </v-card>
      </v-dialog>

      <!--Delete user dialog-->
      <v-dialog v-model="dialogDeleteUser" :max-width="variablesStore.dialogMaxWidth">
        <v-card prepend-icon="mdi-account-remove-outline" title="Delete User">
          <v-progress-circular
            indeterminate
            class="mx-auto"
            v-if="usersList == undefined"
          ></v-progress-circular>
          <v-list lines="two" v-else>
            <v-list-subheader>Select Users to delete</v-list-subheader>
            <v-list-item
              prepend-icon="mdi-account-circle-outline"
              v-for="user in usersList"
              :key="user.id"
              :title="user.username"
              :subtitle="user.email"
              @click="openWarningDeleteDialog(user.id, user.username)"
            >
              <template v-slot:append>
                <v-icon icon="mdi-delete-outline" />
              </template>
            </v-list-item>
          </v-list>
          <v-divider v-if="usersList != undefined"></v-divider>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn text="Done" variant="tonal" @click="dialogDeleteUser = false"></v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <v-dialog v-model="dialogWarnDeleteUser" :max-width="variablesStore.errorMaxWidth">
        <v-card
          color="warning"
          prepend-icon="mdi-alert"
          title="Are you sure?"
          :text="
            'Do you really want to delete user ' +
            deletingUserName +
            '? This action cannot be undone'
          "
        >
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn text="Back" @click="dialogWarnDeleteUser = false"></v-btn>
            <v-btn text="Delete" variant="tonal" @click="confirmDeleteUser(deletingUserID)"></v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <!--New project dialog-->
      <v-dialog v-model="dialogCreateProject" :max-width="variablesStore.dialogMaxWidth">
        <v-card prepend-icon="mdi-plus" title="Create New Project">
          <v-form
            @submit.prevent="submitNewProject"
            v-model="validNewProjectData"
            :rules="rulesCreateProject"
          >
            <v-card-text>
              <v-row dense>
                <v-col cols="12" md="9" sm="9">
                  <v-text-field
                    label="Project Name"
                    required
                    v-model="projectName"
                    :rules="rulesCreateProject"
                  />
                </v-col>

                <v-col cols="12" md="3" sm="3" class="d-flex justify-center">
                  <v-checkbox label="Is Active" class="ml-2" v-model="isProjectActive"></v-checkbox>
                </v-col>

                <v-col cols="12">
                  <v-progress-circular
                    indeterminate
                    v-if="usersList == undefined"
                  ></v-progress-circular>
                  <v-list v-else>
                    <v-list-subheader>Select Users</v-list-subheader>
                    <v-list-item v-for="user in usersList" :key="user.id">
                      <!--Prepend checkbox for project inclusion-->
                      <template v-slot:prepend>
                        <v-list-item-action>
                          <v-checkbox-btn
                            v-model="projectUsersList"
                            :value="user.id"
                          ></v-checkbox-btn>
                        </v-list-item-action>
                      </template>

                      <template v-slot:append>
                        <v-list-item-action>
                          <v-switch
                            v-model="adminUsersList"
                            hide-details
                            hint="Is Project Admin?"
                            persistent-hint
                            :label="isProjectAdminDisplay(user.id)"
                            :value="user.id"
                            :disabled="isAdminButtonDisabled(user.id)"
                          ></v-switch>
                        </v-list-item-action>
                      </template>

                      <v-list-item-title>{{ user.username }}</v-list-item-title>
                      <v-list-item-subtitle> {{ user.email }}</v-list-item-subtitle>
                    </v-list-item>
                  </v-list>
                </v-col>
                <small class="text-caption text-medium-emphasis"
                  >These users will be able to access this project.</small
                >
              </v-row>
            </v-card-text>

            <v-divider></v-divider>

            <v-card-actions>
              <v-spacer></v-spacer>

              <v-btn text="Cancel" variant="plain" @click="dialogCreateProject = false"></v-btn>

              <v-btn
                color="primary"
                text="Create"
                variant="tonal"
                type="submit"
                :loading="loadingCreateProject"
              ></v-btn>
            </v-card-actions>
          </v-form>
        </v-card>
      </v-dialog>
      <router-view :key="$route.path" @openNewProject="dialogCreateProject = true"></router-view>
    </v-main>
  </v-app>
</template>
