<script>
import DynamicButton from './dynamic-button.vue'
import { useLoginStore, useNewTaskStore, useVariablesStore } from '@/store'
import DialogConfirm from '../dialogs/dialog-confirm.vue'
import DialogGeneric from '@/components/dialogs/dialog-generic.vue'
import dataService from '@/components/dataService.js'

export default {
  components: {
    DialogGeneric,
    ConfirmDialog: DialogConfirm,
    DynamicButton
  },
  data() {
    return {
      variablesStore: useVariablesStore(),
      newTaskStore: useNewTaskStore(),
      loginStore: useLoginStore(),
      dialogDocs: false,
      dialogUsers: false,
      loadingEditUsers: false,
      dialogNewTask: false
    }
  },
  emits: ['refresh'],
  props: {
    title: String,
    id: Number,
    isActive: Boolean
  },
  methods: {
    async deleteProject() {
      if (
        await this.$refs.confirm.open('Confirm', 'Are you sure you want to delete this record?')
      ) {
        dataService.deleteProject(this.id).then(() => {
          this.$emit('refresh')
        })
      }
    },
    manageDocs: function () {
      this.dialogDocs = true
    },

    manageUsers: function () {
      this.dialogUsers = true
    },

    // manageTasks: function () {
    //   this.dialogNewTask = true
    // },

    openTaskList: function (id) {
      this.$router.push({
        name: 'tasks',
        params: { projectID: id }
      })
    }
  }
}
</script>

<template>
  <ConfirmDialog ref="confirm"></ConfirmDialog>
  <DialogGeneric
    v-if="loginStore.is_admin || loginStore.project_manager.includes(id)"
    v-model="dialogDocs"
    component-file="./dialog-manage-docs.vue"
    :data="{ id: id }"
  ></DialogGeneric>
  <DialogGeneric
    v-if="loginStore.is_admin"
    v-model="dialogUsers"
    component-file="./dialog-manage-users.vue"
    :data="{ id: id }"
  ></DialogGeneric>

  <v-list-item
    @click.prevent="openTaskList(id)"
    :title="title"
    :subtitle="`Project ID: ${id}. Project ${isActive ? 'Active' : 'Inactive'}`"
  >
    <template v-slot:append>
      <DynamicButton
        class="ms-3"
        :icon="'mdi-location-enter'"
        :text="'Enter'"
        color="info"
        @click.stop="openTaskList(id)"
      />
      <DynamicButton
        class="ms-3"
        v-if="loginStore.is_admin || loginStore.project_manager.includes(id)"
        :icon="'mdi-file-document-multiple-outline'"
        :text="'Docs'"
        @click.stop="manageDocs(id)"
      />
      <DynamicButton
        class="ms-3"
        v-if="loginStore.is_admin"
        :icon="'mdi-account-circle-outline'"
        :text="'Users'"
        @click.stop="manageUsers()"
      />
      <DynamicButton
        class="ms-3"
        v-if="loginStore.is_admin"
        :icon="'mdi-trash-can-outline'"
        :text="'Delete'"
        color="error"
        @click.stop="deleteProject()"
      />
    </template>
  </v-list-item>
</template>
