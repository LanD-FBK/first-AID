<script>
import DynamicButton from '@/components/singleFileComponents/dynamic-button.vue'

export default {
  name: 'TaskAnnotations',
  components: {
    DynamicButton
  },
  emits: ['closeAnnotation', 'addAnnotation', 'reopenAnnotation', 'editAnnotation'],
  props: {
    annotations: Object,
    task: Object,
    isManager: Boolean,
    depth: Number,
    step: {
      type: Number,
      default: 30
    }
  },
  methods: {
    closeAnnotation: function (task_id, id) {
      this.$emit('closeAnnotation', task_id, id)
    },
    reopenAnnotation: function (task_id, id) {
      this.$emit('reopenAnnotation', task_id, id)
    },
    addAnnotation: function (task_id, parent) {
      this.$emit('addAnnotation', task_id, parent)
    },
    editAnnotation: function (task_id, annotation_id) {
      this.$emit('editAnnotation', task_id, annotation_id)
    }
  }
}
</script>

<template>
  <template v-for="annotation in annotations" :key="annotation.id">
    <v-list-item
      :style="{ 'margin-left': depth + 'px' }"
      :title="annotation.title"
      :subtitle="annotation.id + ' - ' + annotation.subtitle"
    >
      <template v-slot:prepend>
        <v-avatar :color="annotation.closed ? 'grey-lighten-1' : 'yellow-lighten-1'">
          <v-icon>mdi-text-box</v-icon>
        </v-avatar>
      </template>
      <template v-slot:append v-if="task.is_active">
        <DynamicButton
          class="ms-3"
          v-if="annotation.closed"
          text="Add annotation"
          color="blue-lighten-1"
          icon="mdi-text-box-plus"
          @click="addAnnotation(task.id, annotation.id)"
        ></DynamicButton>
        <DynamicButton
          class="ms-3"
          v-else
          color="yellow-lighten-1"
          text="Edit annotation"
          icon="mdi-pencil"
          @click="editAnnotation(task.id, annotation.id)"
        ></DynamicButton>
        <DynamicButton
          class="ms-3"
          v-if="isManager && annotation.closed"
          color="yellow-lighten-1"
          text="Reopen annotation"
          icon="mdi-text-box-edit"
          @click="reopenAnnotation(task.id, annotation.id)"
        ></DynamicButton>
        <DynamicButton
          class="ms-3"
          v-else
          color="yellow-lighten-1"
          text="Confirm annotation"
          icon="mdi-text-box-check"
          @click="closeAnnotation(task.id, annotation.id)"
        ></DynamicButton>
      </template>
    </v-list-item>

    <TaskAnnotations
      :is-manager="isManager"
      :task="task"
      @close-annotation="closeAnnotation"
      @reopen-annotation="reopenAnnotation"
      @add-annotation="addAnnotation"
      @edit-annotation="editAnnotation"
      v-if="annotation.children"
      :annotations="annotation.children"
      :depth="step + depth"
    >
    </TaskAnnotations>
  </template>
</template>

<style scoped></style>
