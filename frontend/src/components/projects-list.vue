<script>
import { useVariablesStore, useLoginStore } from '@/store'
import dataService from './dataService'
import ListItem from './singleFileComponents/project-list-item.vue'
import DialogGeneric from '@/components/dialogs/dialog-generic.vue'

export default {
  components: {
    ListItem,
    DialogGeneric
  },
  data() {
    return {
      usersList: undefined,
      showBase: false,
      showDialogCreateProject: false,
      variablesStore: useVariablesStore(),
      loginStore: useLoginStore(),
      ds: dataService,
      projects: undefined
    }
  },
  mounted: function () {
    this.updateProjects()
    if (this.loginStore.is_admin) {
      this.updateUsers()
    }
  },
  methods: {
    updateUsers: function () {
      const self = this
      dataService.getUsers().then(function (data) {
        self.usersList = data.data
      })
    },
    updateProjects: function () {
      const self = this
      self.projects = undefined
      dataService.getProjects().then(function (data) {
        self.projects = data.data
      })
    }
  }
}
</script>

<template>
  <div>
    <DialogGeneric
      v-if="loginStore.is_admin"
      v-model="showDialogCreateProject"
      component-file="./dialog-create-project.vue"
      @refresh="updateProjects"
      :data="{ usersList: usersList }"
    ></DialogGeneric>

    <v-container>
      <template v-if="projects === undefined">
        <v-row>
          <v-col cols="6">
            <v-skeleton-loader type="heading"></v-skeleton-loader>
          </v-col>
          <v-col cols="6" class="text-right">
            <v-skeleton-loader
              class="mx-auto d-flex flex-row-reverse project-loader-buttons"
              type="button"
            ></v-skeleton-loader>
          </v-col>
          <v-col cols="12">
            <v-skeleton-loader
              type="list-item-avatar-two-line, list-item-avatar-two-line, list-item-avatar-two-line, list-item-avatar-two-line"
            ></v-skeleton-loader>
          </v-col>
        </v-row>
      </template>
      <template v-else>
        <v-row justify="center">
          <v-col cols="6">
            <p class="mt-3 text-h5 font-weight-bold">Projects</p>
          </v-col>
          <v-col cols="6" class="text-end">
            <div class="mt-3">
              <v-btn
                color="primary"
                variant="elevated"
                prepend-icon="mdi-plus-circle"
                @click="showDialogCreateProject = true"
                v-if="loginStore.is_admin"
                >Add Project
              </v-btn>
            </div>
          </v-col>
          <v-col cols="12" align="center"></v-col>
        </v-row>
        <v-card>
          <v-list lines="two">
            <ListItem
              v-for="project of projects"
              :key="project.id"
              :title="project.name"
              :users="project.users"
              :id="project.id"
              :isActive="project.is_active"
              @refresh="updateProjects"
            />
          </v-list>
        </v-card>
      </template>
    </v-container>
  </div>
</template>
