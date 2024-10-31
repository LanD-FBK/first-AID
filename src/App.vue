<script>
import dataService from './components/dataService'
import { useLoginStore, useVariablesStore, useNewTaskStore } from './store'

export default {
  data() {
    return {
      ds: dataService,
      loginStore: useLoginStore(),
      variablesStore: useVariablesStore(),
      newTaskStore: useNewTaskStore(),
      usersList: undefined,
      newTaskStatus: {
        isDialogActive: false, 
        users: undefined, 
        files: undefined
      },

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
      confirmDeleteUserLoading: false,

      //New Task vars
      //dialogNewTask: false,
      loadingSubmitNewTask: false,
      snackbarNewTaskSuccess: false,
      dialogNewTaskError: false,
      dialogNewTaskErrorMessage: '',
      validNewTaskData: false,
      rulesNewTask: [
        function (value) {
          if (value) return true
          return 'Please provide a task name'
        }
      ],
      taskName: '',
      isNewTaskActive: false,
      selectedTaskLanguage: undefined,
      initialDataTaskSelection: undefined,
      newTurnTaskSelection: undefined,
      newTaskUsers: [],
      newTaskFiles: [],

      //Initial data vars
      //No further Axios configuration necessary.
      //baseURL does not apply if a full URL is supplied
      initialDataEndpoint: '',
      initialDataMethods: [],
      initialDataRoles: [],
      initialDataButtonLoading: false,
      initialDataError: false,
      initialDataErrorStatus: '',
      selectedInitialDataGenerationMethod: undefined,

      //New turn vars
      newTurnEndpoint: '',
      newTurnError: false,
      newTurnErrorMessage: '',
      newTurnButtonLoading: false,
      selectedNewTurnGenerationMethod: undefined,
      newTurnMethods: [],
      newTurnRoles: [],

      dialogDifferentMethodsError: false,
      //Roles vars
      newTaskRoles: [
        {
          name: '',
          id: '',
          ground: false,
          number: 0
        },
        {
          name: '',
          id: '',
          ground: true,
          number: 1
        }
      ],
      users: undefined,
      files: undefined,

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
            self.errorUserDialogText = String(error.message + ": " + error.response.statusText)
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
              self.errorUserDialogText = String(error.message + ": " + error.response.statusText)
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
              self.errorUserDialogText = String(error.message + ": " + error.response.statusText)
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
          self.errorUserDialogText = String(error.message + ": " + error.response.statusText)
        })
    },

    //Consider merge in one function
    //Initial Data retrieval and handling
    getInitialData: function () {
      this.initialDataButtonLoading = true
      const self = this
      self.initialDataRoles = []
      self.initialDataMethods = []
      dataService
        .getTaskData(this.initialDataEndpoint)
        .then(function (data) {
          //May need to be changed if APIs change
          for (let item of data.data) {
            self.initialDataRoles.push({
              generationMethod: item.generation_method,
              roles: item.roles
            })
            console.log(self.initialDataRoles)
            self.initialDataMethods.push({
              title: item.generation_method,
              props: {
                disabled: false
              }
            })
          }
          self.initialDataButtonLoading = false
        })
        .catch(function (error) {
          console.log(error)
          self.initialDataButtonLoading = false
          self.initialDataError = true
          self.initialDataErrorStatus = String(error.message + ": " + error.response.statusText)
        })
    },
    //New turn Data retrieval and handling
    getNewTurn: function () {
      this.newTurnButtonLoading = true
      const self = this
      self.newTurnMethods = []
      self.newTurnRoles = []
      dataService
        .getTaskData(this.newTurnEndpoint)
        .then(function (data) {
          console.log(data.data)
          for (let item of data.data) {
            self.newTurnRoles.push({
              generationMethod: item.generation_method,
              roles: item.roles
            })
            self.newTurnMethods.push({
              title: item.generation_method,
              props: {
                disabled: false
              }
            })
          }
          console.log(self.newTurnMethods)
          self.newTurnButtonLoading = false
        })
        .catch(function (error) {
          console.log(error)
          self.newTurnButtonLoading = false
          self.newTurnError = true
          self.newTurnErrorMessage = String(error.message + ": " + error.response.statusText)
        })
    },

    //Send new task to API
    submitNewTask: function () {
      if (this.validNewTaskData) {
        this.loadingSubmitNewTask = true
        const self = this
        let meta = {}
        let sendNewTaskRoles = []
        for (let role of this.newTaskRoles) {
          sendNewTaskRoles.push({
            label: role.id,
            name: role.name,
            ground: role.ground
          })
        }
        if (this.selectedInitialDataGenerationMethod != undefined) {
          if (this.selectedNewTurnGenerationMethod != undefined) {
            //Both 'Initial Data' and 'New Turn' call APIs
            meta = {
              start_type_url: this.initialDataEndpoint,
              start_type_method: this.selectedInitialDataGenerationMethod,
              inside_type_endpoint: this.newTurnEndpoint,
              inside_type_api: this.selectedNewTurnGenerationMethod
            }
          } else {
            //Only 'Initial Data' calls APIs
            meta = {
              start_type_url: this.initialDataEndpoint,
              start_type_method: this.selectedInitialDataGenerationMethod
            }
          }
        } else if (this.selectedNewTurnGenerationMethod != undefined) {
          //Only 'New Turn' calls APIs
          meta = {
            inside_type_endpoint: this.newTurnEndpoint,
            inside_type_api: this.selectedNewTurnGenerationMethod
          }
        }
        dataService
          .addTaskToProject(
            this.id,
            this.taskName,
            this.initialDataTaskSelection,
            this.newTurnTaskSelection,
            this.selectedTaskLanguage,
            this.isNewTaskActive,
            meta,
            sendNewTaskRoles,
            this.newTaskUsers,
            this.newTaskFiles
          )
          .then(function (data) {
            console.log(data)
            self.dialogNewTask = false
            self.snackbarNewTaskSuccess = true
            self.loadingSubmitNewTask = false
          })
          .catch(function (error) {
            console.log(error)
            self.dialogNewTaskError = true
            self.dialogNewTaskErrorMessage = String(error.message + ": " + error.response.statusText)
            self.loadingSubmitNewTask = false
          })
      }
    },

    //Add new role to new task
    addNewRole: function () {
      this.newTaskRoles.push({
        name: '',
        id: '',
        number: this.newTaskRoles[this.newTaskRoles.length - 1].number + 1
      })
      console.log(this.newTaskRoles)
    },

    //Removes role from new task
    deleteRole: function (deleteIndex) {
      this.newTaskRoles.splice(deleteIndex, 1)
      console.log(this.newTaskRoles)
    },

    editProjectDialogAdminDisplay: function (userID) {
      if (this.editProjectAdminList.includes(userID)) return 'Admin User'
      return 'Normal User'
    },
    //Check logic
    isNewTurnMethodsListItemDisabled: function (generationMethod) {
      console.log(this.selectedInitialDataGenerationMethod)
      console.log(generationMethod)
      if (this.selectedInitialDataGenerationMethod == '') return false
      else if (this.selectedInitialDataGenerationMethod == generationMethod) return false
      return true
    },
    //Check logic
    isInitialDataMethodsListItemDisabled: function (generationMethod) {
      if (this.selectedNewTurnGenerationMethod == '') return false
      else if (this.selectedNewTurnGenerationMethod != generationMethod) return false
      return true
    }
  },
  computed: {
    isProjectsList() {
      return this.$route.name == 'projects' ? true : false
    },
    isAdmin() {
      return this.loginStore.username == 'admin' ? true : false
    },
    isInitialDataFormDisabled() {
      console.log(this.initialDataTaskSelection)
      return this.initialDataTaskSelection === 'pre_compiled' ? false : true
    },
    isNewTurnFormDisabled() {
      return this.newTurnTaskSelection === 'choice' ? false : true
    },
    isInitialDataSelectionDisabled() {
      if (this.initialDataMethods.length == 0 || this.isInitialDataFormDisabled) return true
      return false
    },
    isNewTurnSelectionDisabled() {
      if (this.newTurnMethods.length == 0 || this.isNewTurnFormDisabled) return true
      return false
    },

    //Check logic
    isNewTaskRolesDisabled() {
      if (this.initialDataTaskSelection == undefined || this.newTurnTaskSelection == undefined)
        return true
      else if (!this.isInitialDataFormDisabled || !this.isNewTurnFormDisabled) return true
      return false
      /* if (this.initialDataTaskSelection == undefined || this.newTurnTaskSelection == undefined)
        return true
      else if (
        (!this.isInitialDataFormDisabled &&
          this.selectedInitialDataGenerationMethod == undefined) ||
        (!this.isNewTurnFormDisabled && this.selectedNewTurnGenerationMethod == undefined)
      )
        return true
      return false */
    },
    isNewTaskRolesDeleteDisabled() {
      if (this.newTaskRoles.length <= 2) return true
      return false
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
    },

    //Not working, check why
    selectedInitialDataGenerationMethod(newValue, oldValue) {
      if (newValue != undefined) {
        if (
          this.selectedNewTurnGenerationMethod == undefined ||
          newValue == this.selectedNewTurnGenerationMethod
        ) {
          for (let item of this.initialDataRoles) {
            if (item.generationMethod == newValue) {
              //"Deletes" the 'newTaskRoles' array
              this.newTaskRoles.splice(0, this.newTaskRoles.length)
              for (let role of item.roles) {
                let i = 0
                this.newTaskRoles.push({
                  name: role.name,
                  id: role.label,
                  ground: role.ground,
                  number: i
                })
                i++
              }
            }
          }
        } else {
          this.dialogDifferentMethodsError = true
        }
      }
    },
    initialDataTaskSelection(newValue, oldValue){
      if(newValue == 'empty' && oldValue !== undefined){
        console.log('watcher empty')
        for (let role of this.newTaskRoles){
          role.id = ''
          role.name = ''
        }
        this.initialDataEndpoint = ''
      }
    },
    selectedNewTurnGenerationMethod(newValue, oldValue) {
      if (newValue != undefined) {
        if (
          this.selectedInitialDataGenerationMethod == undefined ||
          this.selectedInitialDataGenerationMethod == newValue
        ) {
          for (let item of this.newTurnRoles) {
            if (item.generationMethod == newValue) {
              this.newTaskRoles.splice(0, this.newTaskRoles.length)
              for (let role of item.roles) {
                let i = 0
                this.newTaskRoles.push({
                  name: role.name,
                  id: role.label,
                  ground: role.ground,
                  number: i
                })
                i++
              }
            }
          }
        } else {
          this.dialogDifferentMethodsError = true
        }
      }
    },
    dialogDifferentMethodsError(newValue, oldValue) {
      if (newValue == true) {
        this.selectedInitialDataGenerationMethod = undefined
        this.selectedNewTurnGenerationMethod = undefined
        this.newTaskRoles = [
          {
            name: '',
            id: '',
            ground: false,
            number: 0
          },
          {
            name: '',
            id: '',
            ground: true,
            number: 1
          }
        ]
      }
    }
  },
  provide(){
    return{
      newTaskStatus: this.newTaskStatus
    }
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
      <v-btn @click="this.newTaskStatus.isDialogActive = true">{{ String(this.newTaskStatus.isDialogActive) }}</v-btn>
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
          <v-btn color="blue" variant="text" @click="successNewUserSnackbar = false"> Close </v-btn>
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

          <!--New Task Dialog-->
    <v-dialog v-model="newTaskStatus.isDialogActive" max-width="90%">
      <v-card title="Add New Task" prepend-icon="mdi-file-document-plus-outline">
        <v-form v-model="validNewTaskData" :rules="rulesNewTask" @submit.prevent="submitNewTask">
          <v-card-text>
            <v-row dense>
              <v-col cols="12" md="8" sm="8">
                <v-text-field label="Task Name" required v-model="taskName" :rules="rulesNewTask" />
              </v-col>

              <v-col cols="12" md="2" sm="2" class="d-flex justify-center">
                <v-select
                  label="Language"
                  v-model="selectedTaskLanguage"
                  :items="newTaskStore.language"
                  item-title="complete"
                  item-value="apiFormat"
                />
              </v-col>
              <v-col cols="12" md="2" sm="2" class="d-flex justify-center">
                <v-checkbox label="Is Active" v-model="isNewTaskActive"></v-checkbox>
              </v-col>

              <!--Users list-->
              <v-col cols="6">
                <v-list height="200px">
                  <v-list-subheader>Select users</v-list-subheader>
                  <v-list-item
                    v-for="user in users"
                    :key="user.user.id"
                    :title="user.user.username"
                    :subtitle="user.user.email"
                  >
                    <template v-slot:prepend>
                      <v-list-item-action>
                        <v-checkbox-btn v-model="newTaskUsers" :value="user.user.id" />
                      </v-list-item-action>
                    </template>
                  </v-list-item>
                </v-list>
              </v-col>

              <!--Files list-->
              <v-col cols="6">
                <v-list height="200px">
                  <v-list-subheader>Select files</v-list-subheader>
                  <v-list-item
                    v-for="file of files"
                    :key="file.id"
                    :title="file.name"
                    :subtitle="'File ID: ' + file.id"
                  >
                    <template v-slot:prepend>
                      <v-list-item-action>
                        <v-checkbox-btn v-model="newTaskFiles" :value="file.id" />
                      </v-list-item-action>
                    </template>
                  </v-list-item>
                </v-list>
              </v-col>

              <!--Initial Data and New Turn-->
              <v-col cols="6">
                <v-select
                  label="Initial Data"
                  v-model="initialDataTaskSelection"
                  :items="newTaskStore.initialData"
                  item-title="complete"
                  item-value="apiFormat"
                ></v-select>
                <!-- text-field and select are enabled only when initial data is 'pre-filled'-->
                <v-text-field
                  v-model="initialDataEndpoint"
                  label="URL"
                  :disabled="isInitialDataFormDisabled"
                  :error="initialDataError"
                  :error-messages="initialDataErrorStatus"
                >
                  <template v-slot:append>
                    <v-btn
                      text="Go"
                      @click="getInitialData()"
                      variant="tonal"
                      :loading="initialDataButtonLoading"
                    />
                  </template>
                </v-text-field>
                <v-select
                  v-model="selectedInitialDataGenerationMethod"
                  label="Generation Method"
                  :items="initialDataMethods"
                  :disabled="isInitialDataSelectionDisabled"
                ></v-select>
              </v-col>
              <v-col cols="6">
                <v-select
                  label="New Turn"
                  v-model="newTurnTaskSelection"
                  :items="newTaskStore.newTurn"
                  item-title="complete"
                  item-value="apiFormat"
                ></v-select>
                <v-text-field
                  v-model="newTurnEndpoint"
                  label="URL"
                  :disabled="isNewTurnFormDisabled"
                  :error="newTurnError"
                  :error-messages="newTurnErrorMessage"
                >
                  <template v-slot:append>
                    <v-btn
                      text="Go"
                      @click="getNewTurn()"
                      variant="tonal"
                      :loading="newTurnButtonLoading"
                    />
                  </template>
                </v-text-field>
                <v-select
                  v-model="selectedNewTurnGenerationMethod"
                  label="Generation Method"
                  :items="newTurnMethods"
                  :disabled="isNewTurnSelectionDisabled"
                ></v-select>
              </v-col>

              <!--Roles list-->
              <v-col cols="12">
                <!--
                <p class="text-body-1 mt-2">Roles</p>
                -->
                <!--TODO: set max height on container in order to avoid card buttons disappearing-->
                <v-container fluid max-heigth="300px">
                  <v-row dense v-for="role in newTaskRoles" :key="role.number">
                    <v-col>
                      <v-text-field
                        v-model="role.id"
                        :disabled="isNewTaskRolesDisabled"
                        label="Speaker ID"
                      >
                        <template v-slot:prepend>
                          <v-tooltip text="Speaker has ground">
                            <template v-slot:activator="{ props }">
                              <v-btn
                                v-bind="props"
                                :icon="role.ground ? 'mdi-file-document-check-outline' : 'mdi-file-document-remove-outline'"
                                :color="role.ground ? 'primary' : ''"
                                @click="role.ground = !role.ground"
                                :disabled="isNewTaskRolesDisabled"
                              />
                            </template>
                          </v-tooltip>
                        </template>
                      </v-text-field>
                    </v-col>
                    <v-col>
                      <v-text-field
                        v-model="role.name"
                        :disabled="isNewTaskRolesDisabled"
                        label="Speaker Role"
                      >
                        <template v-slot:append>
                          <v-btn
                            icon="mdi-trash-can-outline"
                            variant="tonal"
                            @click="deleteRole()"
                            :disabled="isNewTaskRolesDeleteDisabled"
                          />
                        </template>
                      </v-text-field>
                    </v-col>
                  </v-row>
                  <v-btn
                    class="mb-4"
                    :disabled="isNewTaskRolesDisabled"
                    variant="tonal"
                    text="Add New Role"
                    @click="addNewRole()"
                  />
                </v-container>
              </v-col>
            </v-row>
          </v-card-text>
          <v-divider></v-divider>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn text="Cancel" variant="tonal" @click="newTaskStatus.isDialogActive = false" />
            <!--type="submit"-->
            <v-btn
              text="Create"
              type="submit"
              :loading="loadingSubmitNewTask"
              variant="tonal"
              color="primary"
            />
          </v-card-actions>
        </v-form>
      </v-card>
    </v-dialog>
    <v-dialog v-model="dialogDifferentMethodsError" :max-width="variablesStore.errorMaxWidth">
      <v-card
        title="Error!"
        prepend-icon="mdi-alert-circle"
        color="error"
        text="Different Generation Methods are selected!"
      >
        <v-card-actions>
          <v-btn @click="dialogDifferentMethodsError = false" text="Close"></v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="dialogNewTaskError" :max-width="variablesStore.errorMaxWidth">
      <v-card
        title="Error!"
        prepend-icon="mdi-alert-circle"
        color="error"
        :text="'Error! ' + dialogNewTaskErrorMessage"
      >
        <v-card-actions>
          <v-btn @click="dialogNewTaskError = false" text="Close"></v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-snackbar v-model="snackbarNewTaskSuccess" timeout="2000"
      >New Task created successfully!
      <template v-slot:actions>
        <v-btn color="blue" variant="text" @click="snackbarNewTaskSuccess = false"> Close </v-btn>
      </template>
    </v-snackbar>
      <router-view :key="$route.path" @openNewProject="dialogCreateProject = true"></router-view>
    </v-main>
  </v-app>
</template>
