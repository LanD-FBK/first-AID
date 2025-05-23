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

    <v-container fluid v-if="projects === undefined">
      <v-row>
        <v-col cols="12" class="text-center">
          <v-progress-circular indeterminate class="mx-auto" :size="128"></v-progress-circular>
        </v-col>
      </v-row>
    </v-container>
    <v-container fluid v-else>
      <v-row justify="center">
        <v-col cols="6">
          <p class="text-h5 font-weight-bold">Projects</p>
        </v-col>
        <v-col cols="6" align="right">
          <v-btn
            color="primary"
            variant="elevated"
            @click="showDialogCreateProject = true"
            v-if="loginStore.is_admin"
            >Add Project
          </v-btn>
        </v-col>
        <v-col cols="12" align="center"></v-col>
      </v-row>
      <template v-for="project of projects" :key="project.id">
        <ListItem
          :title="project.name"
          :users="project.users"
          :id="project.id"
          :isActive="project.is_active"
          @refresh="updateProjects"
        />
      </template>
    </v-container>
  </div>
</template>
