<script>
import { useNewTaskStore, useVariablesStore } from '@/store.js'
import dataService from '../dataService.js'
import DialogConfirm from '../dialogs/dialog-confirm.vue'

export default {
  props: {
    users: Object,
    files: Array,
    projectID: Number
  },
  components: {
    DialogConfirm
  },
  data() {
    return {
      ds: dataService,
      variablesStore: useVariablesStore(),
      //Is this needed?
      newTaskStore: useNewTaskStore(),
      //New Task vars
      loadingSubmitNewTask: false,
      snackbarNewTaskSuccess: false,
      validNewTaskData: false,
      rulesNewTask: [
        function (value) {
          if (value) return true
          return 'Please provide a task name'
        }
      ],
      taskName: '',
      isNewTaskActive: true,
      selectedTaskLanguage: undefined,
      initialDataTaskSelection: undefined,
      newTurnTaskSelection: undefined,
      newTaskUsers: [],
      newTaskFiles: [],

      //Initial data vars
      initialDataEndpoint: '',
      initialDataMethods: [],
      initialDataRoles: [],
      initialDataButtonLoading: false,
      selectedInitialDataGenerationMethod: undefined,

      //New turn vars
      newTurnEndpoint: '',
      newTurnButtonLoading: false,
      selectedNewTurnGenerationMethod: undefined,
      newTurnMethods: [],
      newTurnRoles: [],

      dialogDifferentMethodsError: false,
      newTaskRoles: [],
    }
  },
  mounted: function () {
    this.resetTaskRoles()
  },
  methods: {
    resetTaskRoles: function () {
      this.newTaskRoles = [...this.newTaskStore.initialTaskRoles]
    },
    getData: function (type) {
      console.log(type)
      const self = this
      let endpoint = undefined
      let toAddRoles = undefined
      let toAddMethods = undefined

      if (type === 'initial') {
        self.initialDataButtonLoading = true
        endpoint = self.initialDataEndpoint
        toAddRoles = self.initialDataRoles
        toAddMethods = self.initialDataMethods
      } else if (type === 'new') {
        self.newTurnButtonLoading = true
        endpoint = self.newTurnEndpoint
        toAddRoles = self.newTurnRoles
        toAddMethods = self.newTurnMethods
      } else {
        return
      }

      // Use splice() and not [] because toAddMethods is a reference
      toAddMethods.splice(0)

      dataService
        .getTaskData(endpoint)
        .then(function (data) {
          for (let item of data.data) {
            toAddRoles.push({
              generationMethod: item.generation_method,
              roles: item.roles
            })
            toAddMethods.push({
              title: item.generation_method,
              props: {
                disabled: false
              }
            })
          }
        })
        .catch(function (error) {
          self.$refs.confirm.open('Error', error.message + '<br />' + error.response.statusText, {
            noconfirm: true
          })
        })
        .then(function () {
          if (type === 'initial') {
            self.initialDataButtonLoading = false
          } else if (type === 'new') {
            self.newTurnButtonLoading = false
          }
        })
    },

    //Send new task to API
    submitNewTask: function () {
      const self = this
      if (this.validNewTaskData) {
        this.loadingSubmitNewTask = true
        let meta = {}
        let sendNewTaskRoles = []
        for (let role of this.newTaskRoles) {
          sendNewTaskRoles.push({
            label: role.id,
            name: role.name,
            ground: role.ground
          })
        }
        if (this.selectedInitialDataGenerationMethod !== undefined) {
          Object.assign(meta, {
            start_type_url: this.initialDataEndpoint,
            start_type_method: this.selectedInitialDataGenerationMethod
          })
        }
        if (this.selectedNewTurnGenerationMethod !== undefined) {
          Object.assign(meta, {
            inside_type_endpoint: this.newTurnEndpoint,
            inside_type_api: this.selectedNewTurnGenerationMethod
          })
        }
        dataService
          .addTaskToProject(
            this.projectID,
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
          .then(function () {
            self.$emit('exit')
          })
          .catch(function (error) {
            let errorMsg = error.message
            if (error?.response?.statusText) {
              errorMsg += "<br />" + error.response.statusText
            }
            if (error?.response?.data?.detail) {
              errorMsg += "<br />" + error.response.data.detail
            }
            self.$refs.confirm.open('Error', errorMsg, {
              noconfirm: true
            })
          })
          .then(function () {
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
    },

    //Removes role from new task
    deleteRole: function (deleteIndex) {
      this.newTaskRoles.splice(deleteIndex, 1)
    }
  },
  computed: {
    isInitialDataFormDisabled() {
      return this.initialDataTaskSelection !== 'pre_compiled'
    },
    isNewTurnFormDisabled() {
      return this.newTurnTaskSelection !== 'choice'
    },
    isInitialDataSelectionDisabled() {
      return this.initialDataMethods.length === 0 || this.isInitialDataFormDisabled
    },
    isNewTurnSelectionDisabled() {
      return this.newTurnMethods.length === 0 || this.isNewTurnFormDisabled
    },

    //Check logic
    isNewTaskRolesDisabled() {
      if (this.initialDataTaskSelection === undefined || this.newTurnTaskSelection === undefined) {
        return true
      } else if (!this.isInitialDataFormDisabled || !this.isNewTurnFormDisabled) {
        return true
      }
      return false
    },
    isNewTaskRolesDeleteDisabled() {
      return this.newTaskRoles.length <= 2;

    }
  },
  watch: {
    selectedInitialDataGenerationMethod(newValue) {
      if (newValue !== undefined) {
        if (
          this.selectedNewTurnGenerationMethod === undefined ||
          newValue === this.selectedNewTurnGenerationMethod
        ) {
          for (let item of this.initialDataRoles) {
            if (item.generationMethod === newValue) {
              this.newTaskRoles = []
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
          self.$refs.confirm.open('Error', "Cannot select different generation methods", {
            noconfirm: true
          })
        }
      }
    },
    initialDataTaskSelection(newValue) {
      if (
        (this.initialDataTaskSelection === 'empty' ||
          this.initialDataTaskSelection === undefined) &&
        (this.newTurnTaskSelection === 'clean' || this.newTurnTaskSelection === undefined)
      ) {
        this.resetTaskRoles()
      }

      if (newValue === 'empty') {
        this.initialDataMethods = []
        this.initialDataEndpoint = ''
        this.selectedInitialDataGenerationMethod = undefined
      }
      if (newValue === 'clean') {
        this.newTurnMethods = []
        this.newTurnEndpoint = ''
        this.selectedNewTurnGenerationMethod = undefined
      }
    },
    selectedNewTurnGenerationMethod(newValue) {
      if (newValue !== undefined) {
        if (
          this.selectedInitialDataGenerationMethod === undefined ||
          this.selectedInitialDataGenerationMethod === newValue
        ) {
          for (let item of this.newTurnRoles) {
            if (item.generationMethod === newValue) {
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
          self.$refs.confirm.open('Error', "Cannot select different generation methods", {
            noconfirm: true
          })
        }
      }
    },
    dialogDifferentMethodsError() {
      this.resetTaskRoles()
    }
  }
}
</script>

<template>
  <v-card title="Add New Task" prepend-icon="mdi-file-document-plus-outline">
    <DialogConfirm ref="confirm"></DialogConfirm>
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
                v-for="user in this.users"
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
            >
              <template v-slot:append>
                <v-btn
                  text="Go"
                  @click="getData('initial')"
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
            >
              <template v-slot:append>
                <v-btn
                  text="Go"
                  @click="getData('new')"
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
                            :icon="
                              role.ground
                                ? 'mdi-file-document-check-outline'
                                : 'mdi-file-document-remove-outline'
                            "
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
        <v-btn text="Cancel" variant="tonal" @click="$emit('exit')" />
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

  <!--    <v-snackbar v-model="snackbarNewTaskSuccess" timeout="2000"-->
  <!--      >New Task created successfully!-->
  <!--      <template v-slot:actions>-->
  <!--        <v-btn color="blue" variant="text" @click="snackbarNewTaskSuccess = false"> Close</v-btn>-->
  <!--      </template>-->
  <!--    </v-snackbar>-->
</template>
