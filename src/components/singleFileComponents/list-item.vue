<script>
import dataService from '../dataService'
import DynamicButton from './dynamic-button.vue'
import { useNewTaskStore, useVariablesStore } from '@/store'

export default {
  components: {
    DynamicButton
  },
  data() {
    return {
      variablesStore: useVariablesStore(),
      newTaskStore: useNewTaskStore(),
      dialogDocs: false,
      dialogUsers: false,
      loadingEditUsers: false,
      dialogNewTask: false,

      //Manage Tasks vars
      dialogTasks: false,
      loadingSubmitNewTask: false,
      //TODO: add watcher to empty all fields on dialog closure
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

      files: null,
      uploadedFiles: undefined,

      dialogAddUserToProject: false,
      editProjectAdminList: [],
      editProjectUserSelect: []
    }
  },
  props: {
    title: String,
    users: Object,
    id: Number,
    tasks: Object,
    isActive: Boolean
  },
  //Not used at the moment, consider deleting
  mounted: function () {
    const self = this
  },
  methods: {
    submitManageUsers: function () {
      const self = this
      this.loadingEditUsers = true
      let submitAdminList = []
      let submitUserList = []
      for (let user of this.users) {
        submitUserList.push(user.user_id)
        if (this.editProjectAdminList.includes(user.user_id)) {
          submitAdminList.push(true)
        } else {
          submitAdminList.push(false)
        }
      }
      dataService
        .editProject(this.id, this.title, this.isActive, submitUserList, submitAdminList)
        .then(function (data) {
          self.loadingEditUsers = false
          self.dialogUsers = false
        })
        .catch(function (error) {
          //Gestione errore
        })
    },
    manageDocs: function (projectID) {
      this.dialogDocs = true
      this.files = undefined
    },

    //Document handling
    uploadDocs: function () {
      const self = this
      let files = document.getElementById('uploadFiles').files
      // console.log(files)
      dataService.uploadFiles(this.id, files).then(function (data) {
        console.log(data)
        //Triggers watcher and refreshes files list
        self.files = undefined
      })
        .catch(function (error) {
          console.log(error)
          //TODO: error handling with error dialog component
        })

    },

    removeDocument: function (documentID) {
      const self = this
      dataService.deleteProjectFiles(this.id, documentID).then(function (data) {
        console.log(data)
        //Triggers watcher and refreshes files list
        self.files = undefined
      })
    },

    manageUsers: function () {
      this.dialogUsers = true
      for (let user of this.users) {
        if (user.is_project_admin) {
          this.editProjectAdminList.push(user.user_id)
        }
      }
      // console.log(this.editProjectAdminList)
    },

    //Manage Tasks funcs
    manageTasks: function () {
      this.dialogNewTask = true
    },

    //Consider merge in one function
    //Initial Data retrieval and handling
    getInitialData: function () {
      this.initialDataButtonLoading = true
      const self = this
      dataService
        .getTaskData(this.initialDataEndpoint)
        .then(function (data) {
          //May need to be changed if APIs change
          for (let item of data.data) {
            self.initialDataRoles.push({
              generationMethod: item.generation_method,
              roles: item.roles
            })
            // console.log(self.initialDataRoles)
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
          // console.log(error)
          self.initialDataButtonLoading = false
          self.initialDataError = true
          self.initialDataErrorStatus = String(error.message + ": " + error.response.statusText)
        })
    },
    //New turn Data retrieval and handling
    getNewTurn: function () {
      this.newTurnButtonLoading = true
      const self = this
      dataService
        .getTaskData(this.newTurnEndpoint)
        .then(function (data) {
          // console.log(data.data)
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
          // console.log(self.newTurnMethods)
          self.newTurnButtonLoading = false
        })
        .catch(function (error) {
          // console.log(error)
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
            // console.log(data)
            self.dialogNewTask = false
            self.snackbarNewTaskSuccess = true
            self.loadingSubmitNewTask = false
          })
          .catch(function (error) {
            // console.log(error)
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
      // console.log(this.newTaskRoles)
    },

    //Removes role from new task
    deleteRole: function (deleteIndex) {
      this.newTaskRoles.splice(deleteIndex, 1)
      // console.log(this.newTaskRoles)
    },

    editProjectDialogAdminDisplay: function (userID) {
      if (this.editProjectAdminList.includes(userID)) return 'Admin User'
      return 'Normal User'
    },
    //Check logic
    isNewTurnMethodsListItemDisabled: function (generationMethod) {
      // console.log(this.selectedInitialDataGenerationMethod)
      // console.log(generationMethod)
      if (this.selectedInitialDataGenerationMethod == '') return false
      else if (this.selectedInitialDataGenerationMethod == generationMethod) return false
      return true
    },
    //Check logic
    isInitialDataMethodsListItemDisabled: function (generationMethod) {
      if (this.selectedNewTurnGenerationMethod == '') return false
      else if (this.selectedNewTurnGenerationMethod != generationMethod) return false
      return true
    },
    openTaskList: function (id) {
      this.$router.push({
        name: 'tasks',
        params: { projectID: id }
      })
    }
  },
  computed: {
    displaySize() {
      return this.$vuetify.display.name
    },
    isButton() {
      //If true screen size is 'md' or less, so we need to show icons instead of buttons
      return this.$vuetify.display.mdAndDown ? true : false
    },
    isDeleteButtonEditProjectDialog() {
      return this.editProjectUserSelect.length === 0 ? true : false
    },
    isInitialDataFormDisabled() {
      // console.log(this.initialDataTaskSelection)
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
    editProjectAdminList(newValue, oldValue) {
      console.warn(newValue)
    },
    dialogUsers(newValue, oldValue) {
      this.editProjectAdminList = []
      this.editProjectUserSelect = []
    },
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
    initialDataTaskSelection(newValue, oldValue) {
      if (newValue == 'empty' && oldValue !== undefined) {
        // console.log('watcher empty')
        for (let role of this.newTaskRoles) {
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
    },
    files(newValue, oldValue) {
      const self = this
      if (newValue == undefined) {
        dataService.getProjectFiles(this.id).then(function (data) {
          self.files = data.data
          console.log(self.files)
        })
      }
    }
  }
}
</script>

<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <v-card @click.prevent="openTaskList(id)">
          <v-row align="center">
            <v-col cols="12" sm="3" md="6" xl="6" xs="6">
              <v-row class="d-flex justify-left">
                <v-col>
                  <v-card-title>{{ title }}</v-card-title>
                  <v-card-subtitle>Project ID: {{ id }}. Project {{ isActive ? 'Active' : 'Inactive'
                    }}</v-card-subtitle>
                </v-col>
                <!--
                <v-col>
                  <v-btn
                    icon="mdi-pencil-circle-outline"
                    class="ma-2"
                    variant="plain"
                    @click="console.log('icon')"
                  />
                </v-col>
                -->
              </v-row>
            </v-col>
            <v-col cols="12" lg="6" sm="9" md="6" xl="6" xs="6">
              <v-card-actions>
                <DynamicButton :icon="'mdi-file-document-multiple-outline'" :text="'Manage Docs'"
                  @click.stop="manageDocs(id)" />
                <DynamicButton :icon="'mdi-account-circle-outline'" :text="'Manage Users'"
                  @click.stop="manageUsers()" />
                <DynamicButton :icon="'mdi-format-list-checks'" :text="'Manage Tasks'" @click.stop="manageTasks()" />
                <DynamicButton :icon="'mdi-trash-can-outline'" :text="'Delete'" @click.stop="$emit('deleteProject')" />
              </v-card-actions>
            </v-col>
          </v-row>
        </v-card>
      </v-col>
    </v-row>

    <!--Manage Docs dialog-->
    <!--TODO: add spacer before action buttons-->
    <v-dialog v-model="dialogDocs" :max-width="variablesStore.dialogMaxWidth">
      <v-card prepend-icon="mdi-file-document-multiple-outline" title="Manage Project Documents">
        <v-card-text>
          <!--TODO: center spinner-->
          <v-progress-circular indeterminate class="mx-auto" v-if="files == undefined"></v-progress-circular>
          <template v-else-if="files == 0">
            <v-row>
              <!--TODO: fix spacing-->
              <p class="text-caption text-medium-emphasis">There are no files in this project</p>
            </v-row>
            <v-row>
              <input type="file" multiple id="uploadFiles" class="ma-2">
              </input>
            </v-row>
          </template>
          <template v-else>
            <v-list>
              <v-list-item v-for="file of files" :key="file.id" :title="file.name" :subtitle="'File ID: ' + file.id">
                <template v-slot:append>
                  <!--TODO: add spinner after click to let user know that deletion is in progress-->
                  <v-btn icon="mdi-delete" variant="flat" @click="removeDocument(file.id)" />
                </template>
              </v-list-item>
            </v-list>
            <input type="file" multiple id="uploadFiles" class="ma-2">
            </input>
          </template>
        </v-card-text>
        <v-card-actions>
          <v-btn color="primary" variant="outlined" @click="uploadDocs()">Upload</v-btn>
          <v-btn color="primary" variant="flat" @click="dialogDocs = false">Done</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Manage users dialog-->
    <v-dialog v-model="dialogUsers" :max-width="variablesStore.dialogMaxWidth">
      <v-card prepend-icon="mdi-account-circle-outline" title="Manage Project Users">
        <v-row dense>
          <v-col cols="12">
            <v-list lines="two">
              <v-list-subheader>Select the User to edit</v-list-subheader>
              <v-list-item v-for="user in users" :key="user.user.id">
                <!--Prepend checkbox for project inclusion-->
                <template v-slot:append>
                  <v-list-item-action>
                    <v-switch v-model="editProjectAdminList" hide-details hint="Is Project Admin?" persistent-hint
                      :label="editProjectDialogAdminDisplay(user.user.id)" :value="user.user.id"></v-switch>
                  </v-list-item-action>
                </template>

                <template v-slot:prepend>
                  <v-list-item-action>
                    <v-checkbox-btn v-model="editProjectUserSelect" :value="user.user.id"></v-checkbox-btn>
                  </v-list-item-action>
                </template>

                <v-list-item-title>{{ user.user.username }}</v-list-item-title>
                <v-list-item-subtitle> {{ user.user.email }}</v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-col>
        </v-row>
        <v-divider></v-divider>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text="Remove Users" variant="tonal" color="error" :disabled="isDeleteButtonEditProjectDialog"></v-btn>
          <v-btn text="Add New User" variant="tonal" color="primary" @click="dialogAddUserToProject = true"></v-btn>
          <v-btn text="Done" variant="tonal" @click="submitManageUsers()"></v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="dialogTasks" :max-width="variablesStore.dialogMaxWidth">
      <v-card prepend-icon="mdi-format-list-checks" title="Manage Tasks">
        <v-list lines="two">
          <v-list-subheader>Select the task you wish to edit</v-list-subheader>
          <v-list-item v-for="task of this.tasks" :key="task.id" :title="task.title" :subtitle="task.id">
          </v-list-item>
        </v-list>
        <v-card-actions>
          <v-btn color="primary" variant="elevated" text="Add New" />
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!--New Task Dialog-->
    <v-dialog v-model="dialogNewTask" max-width="90%">
      <v-card title="Add New Task" prepend-icon="mdi-file-document-plus-outline">
        <v-form v-model="validNewTaskData" :rules="rulesNewTask" @submit.prevent="submitNewTask">
          <v-card-text>
            <v-row dense>
              <v-col cols="12" md="8" sm="8">
                <v-text-field label="Task Name" required v-model="taskName" :rules="rulesNewTask" />
              </v-col>

              <v-col cols="12" md="2" sm="2" class="d-flex justify-center">
                <v-select label="Language" v-model="selectedTaskLanguage" :items="newTaskStore.language"
                  item-title="complete" item-value="apiFormat" />
              </v-col>
              <v-col cols="12" md="2" sm="2" class="d-flex justify-center">
                <v-checkbox label="Is Active" v-model="isNewTaskActive"></v-checkbox>
              </v-col>

              <!--Users list-->
              <v-col cols="6">
                <v-list height="200px">
                  <v-list-subheader>Select users</v-list-subheader>
                  <v-list-item v-for="user in users" :key="user.user.id" :title="user.user.username"
                    :subtitle="user.user.email">
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
                  <v-list-item v-for="file of files" :key="file.id" :title="file.name"
                    :subtitle="'File ID: ' + file.id">
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
                <v-select label="Initial Data" v-model="initialDataTaskSelection" :items="newTaskStore.initialData"
                  item-title="complete" item-value="apiFormat"></v-select>
                <!-- text-field and select are enabled only when initial data is 'pre-filled'-->
                <v-text-field v-model="initialDataEndpoint" label="URL" :disabled="isInitialDataFormDisabled"
                  :error="initialDataError" :error-messages="initialDataErrorStatus">
                  <template v-slot:append>
                    <v-btn text="Go" @click="getInitialData()" variant="tonal" :loading="initialDataButtonLoading" />
                  </template>
                </v-text-field>
                <v-select v-model="selectedInitialDataGenerationMethod" label="Generation Method"
                  :items="initialDataMethods" :disabled="isInitialDataSelectionDisabled"></v-select>
              </v-col>
              <v-col cols="6">
                <v-select label="New Turn" v-model="newTurnTaskSelection" :items="newTaskStore.newTurn"
                  item-title="complete" item-value="apiFormat"></v-select>
                <v-text-field v-model="newTurnEndpoint" label="URL" :disabled="isNewTurnFormDisabled"
                  :error="newTurnError" :error-messages="newTurnErrorMessage">
                  <template v-slot:append>
                    <v-btn text="Go" @click="getNewTurn()" variant="tonal" :loading="newTurnButtonLoading" />
                  </template>
                </v-text-field>
                <v-select v-model="selectedNewTurnGenerationMethod" label="Generation Method" :items="newTurnMethods"
                  :disabled="isNewTurnSelectionDisabled"></v-select>
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
                      <v-text-field v-model="role.id" :disabled="isNewTaskRolesDisabled" label="Speaker ID">
                        <template v-slot:prepend>
                          <v-tooltip text="Speaker has ground">
                            <template v-slot:activator="{ props }">
                              <v-btn v-bind="props"
                                :icon="role.ground ? 'mdi-file-document-check-outline' : 'mdi-file-document-remove-outline'"
                                :color="role.ground ? 'primary' : ''" @click="role.ground = !role.ground"
                                :disabled="isNewTaskRolesDisabled" />
                            </template>
                          </v-tooltip>
                        </template>
                      </v-text-field>
                    </v-col>
                    <v-col>
                      <v-text-field v-model="role.name" :disabled="isNewTaskRolesDisabled" label="Speaker Role">
                        <template v-slot:append>
                          <v-btn icon="mdi-trash-can-outline" variant="tonal" @click="deleteRole()"
                            :disabled="isNewTaskRolesDeleteDisabled" />
                        </template>
                      </v-text-field>
                    </v-col>
                  </v-row>
                  <v-btn class="mb-4" :disabled="isNewTaskRolesDisabled" variant="tonal" text="Add New Role"
                    @click="addNewRole()" />
                </v-container>
              </v-col>
            </v-row>
          </v-card-text>
          <v-divider></v-divider>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn text="Cancel" variant="tonal" @click="dialogNewTask = false" />
            <!--type="submit"-->
            <v-btn text="Create" type="submit" :loading="loadingSubmitNewTask" variant="tonal" color="primary" />
          </v-card-actions>
        </v-form>
      </v-card>
    </v-dialog>
    <v-dialog v-model="dialogDifferentMethodsError" :max-width="variablesStore.errorMaxWidth">
      <v-card title="Error!" prepend-icon="mdi-alert-circle" color="error"
        text="Different Generation Methods are selected!">
        <v-card-actions>
          <v-btn @click="dialogDifferentMethodsError = false" text="Close"></v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="dialogNewTaskError" :max-width="variablesStore.errorMaxWidth">
      <v-card title="Error!" prepend-icon="mdi-alert-circle" color="error"
        :text="'Error! ' + dialogNewTaskErrorMessage">
        <v-card-actions>
          <v-btn @click="dialogNewTaskError = false" text="Close"></v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-snackbar v-model="snackbarNewTaskSuccess" timeout="2000">New Task created successfully!
      <template v-slot:actions>
        <v-btn color="blue" variant="text" @click="snackbarNewTaskSuccess = false"> Close </v-btn>
      </template>
    </v-snackbar>
  </v-container>
</template>
