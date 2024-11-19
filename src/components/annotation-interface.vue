<script>
import dataService from './dataService'
import highlightable from '@/components/highlight-table.vue'
import { nextTick } from 'vue'
import { Pane, Splitpanes } from 'splitpanes'
import ConfirmDialog from '@/components/dialogs/dialog-confirm.vue'
import DynamicButton from '@/components/singleFileComponents/dynamic-button.vue'
import { useNewTaskStore } from '@/store.js'
import DialogDialogue from '@/components/dialogs/dialog-dialogue.vue'

export default {
  components: {
    DialogDialogue,
    DynamicButton,
    ConfirmDialog,
    highlightable,
    Splitpanes,
    Pane
  },
  data() {
    return {
      newTaskStore: useNewTaskStore(),
      taskInfo: {},
      annotationID: undefined,
      annotationParent: 0,
      projectID: 0,
      selectedRound: 0,
      selectedFile: 0,
      files: undefined,
      fileContent: undefined,
      loadingFile: false,
      loadingData: true,
      fileContentBuffer: {},
      actorsLabels: undefined,
      actors: undefined,
      actorsIDs: undefined,
      annotation_data: undefined,
      toBeSelected: undefined,
      actorsWithGround: undefined,
      time: 0,
      comment: '',
      commentVisible: false,
      removing: [],
      dialog: [
        {
          name: 'Actor',
          dialog: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.'
        }
      ],
      unsavedChanges: false,
      externalGround: {},

      selectedActorForChoice: undefined,
      showChoiceDialog: false,
      useGroundForChoice: []
    }
  },
  unmounted: function () {
    window.removeEventListener('beforeunload', this.handleBeforeUnload)
  },
  mounted: function () {
    window.addEventListener('beforeunload', this.handleBeforeUnload)

    const vueThis = this
    this.projectID = this.$route.params.projectID
    this.taskID = this.$route.params.taskID
    this.annotationID = this.$route.params.annotationID
    this.annotationParent = this.$route.params.annotationParent

    this.externalGround = { ...this.newTaskStore.initialExternalGround }

    vueThis.actorsLabels = {}
    vueThis.files = {}
    vueThis.actors = []
    vueThis.actorsIDs = {}
    vueThis.time = 0
    vueThis.annotation_data = []
    vueThis.actorsWithGround = new Set()

    let promises = []
    promises.push(dataService.getTaskInfo(this.projectID, this.taskID))
    if (this.annotationID) {
      promises.push(dataService.getAnnotation(this.projectID, this.taskID, this.annotationID))
    } else if (this.annotationParent) {
      promises.push(dataService.getAnnotation(this.projectID, this.taskID, this.annotationParent))
    }

    Promise.all(promises).then(function (result) {
      setInterval(function () {
        vueThis.time += 1
      }, 1000)
      if (vueThis.annotationID) {
        vueThis.time = result[1].data.annotations?.time
        if (!vueThis.time) {
          vueThis.time = 0
        }
      }

      if (vueThis.annotationID || vueThis.annotationParent) {
        vueThis.annotation_data = result[1].data.annotations.data
        vueThis.comment = result[1].data.comment
      } else {
        vueThis.annotation_data = result[0].data?.meta?.new_annotation_data
        if (vueThis.annotation_data === undefined || vueThis.annotation_data.length === 0) {
          vueThis.annotation_data = []
        }
      }

      let actor_index = 0
      for (let a of result[0].data.actors) {
        vueThis.actorsIDs[a.label] = actor_index++
        vueThis.actorsLabels[a.label] = a.name
        if (a.ground) {
          vueThis.actorsWithGround.add(a.label)
        }
      }

      vueThis.actors = result[0].data.actors
      if (vueThis.annotation_data.length > 0) {
        let lastSpeaker = vueThis.annotation_data[vueThis.annotation_data.length - 1].speaker
        vueThis.selectedActorForChoice =
          vueThis.actors[(vueThis.actorsIDs[lastSpeaker] + 1) % vueThis.actors.length].label
      } else {
        vueThis.selectedActorForChoice = vueThis.actors[0].label
      }
      vueThis.taskInfo = result[0].data
      let firstOne = undefined
      for (let f of result[0].data.files) {
        vueThis.files[f.file.id] = f.file
        if (firstOne === undefined) {
          firstOne = f.file.id
        }
      }
      if (firstOne !== undefined) {
        vueThis.selectedFile = firstOne
        vueThis.loadFile()
      }
      vueThis.loadingData = false
    })
  },
  computed: {
    filesForSelect: function () {
      let newList = []
      newList.push({
        title: '[Select file]',
        value: 0
      })
      newList.push({
        title: '[External ground]',
        value: -1
      })
      if (this.files) {
        for (let i in this.files) {
          newList.push({
            title: this.files[i].name,
            subtitle: this.files[i].size + ' bytes',
            value: this.files[i].id
          })
        }
      }
      return newList
    },
    rolesForSelect: function () {
      let newList = []
      for (let i in this.actors) {
        // use base-color
        newList.push({
          title: this.actors[i].name,
          value: this.actors[i].label
        })
      }
      return newList
    }
  },
  beforeRouteLeave: async function () {
    // Inspired by: https://stackoverflow.com/questions/51980296/detect-back-button-in-navigation-guards-of-vue-router
    // and: https://router.vuejs.org/guide/advanced/navigation-guards.html#In-Component-Guards
    if (this.unsavedChanges) {
      if (
        !(await this.$refs.confirm.open(
          'Confirm',
          "If you live this page, you'll loose your job. Are you sure?",
          {
            okText: 'Yes',
            cancelText: 'No',
            noconfirm: false,
            color: 'error'
          }
        ))
      ) {
        return false
      }
    }
  },
  methods: {
    shouldAddFromGround: function (index) {
      let ret = true
      ret = ret && index === this.annotation_data.length - 1
      ret = ret && this.annotation_data[index].text.trim().length === 0
      ret = ret && this.actorsWithGround.has(this.annotation_data[index].speaker)
      ret = ret && this.annotation_data[index].ground.length > 0
      return ret
    },
    addByChoice: function (data) {
      this.unsavedChanges = true
      this.selectedActorForChoice =
        this.actors[(this.actorsIDs[data.speaker] + 1) % this.actors.length].label
      data['text'] = data['turn_text']
      if (this.useGroundForChoice.length > 0) {
        let g = this.annotation_data[this.annotation_data.length - 1].ground
        this.annotation_data.pop()
        data['ground'] = g
      }
      this.annotation_data.push(data)
      this.showChoiceDialog = false
    },
    callDynamicWithGround: function () {
      this.useGroundForChoice = []
      for (let g of this.annotation_data[this.annotation_data.length - 1]['ground']) {
        this.useGroundForChoice.push(g.text)
      }
      this.showChoiceDialog = true
    },
    callDynamic: function () {
      this.useGroundForChoice = []
      this.showChoiceDialog = true
    },
    handleBeforeUnload: function (event) {
      // Inspired by: https://javokhirbekkhaydarov.medium.com/when-user-clicks-close-tab-how-to-show-confirm-modal-in-vuejs-9ef000b8cdf8
      if (this.unsavedChanges) {
        event.preventDefault()
        event.returnValue = 'Are you sure to leave site?'
      }
    },
    addExternalGround: function () {
      this.unsavedChanges = true
      let newGround = {
        text: this.externalGround.text,
        name: this.externalGround.name,
        link: this.externalGround.link,
        file_id: -1
      }
      this.annotation_data[this.selectedRound].ground.push(newGround)
      this.externalGround = { ...this.newTaskStore.initialExternalGround }
    },
    confirmAnnotation: function () {
      let annotation = { data: this.annotation_data, time: this.time }
      let vueThis = this

      if (this.annotationID) {
        dataService
          .editAnnotation(this.projectID, this.taskID, this.annotationID, annotation, this.comment)
          .then(function () {
            vueThis.unsavedChanges = false
            vueThis.$router.push({ name: 'tasks', params: { projectID: vueThis.projectID } })
          })
          .catch(function (error) {
            console.log(error)
          })
      } else {
        dataService
          .createAnnotation(
            this.projectID,
            this.taskID,
            annotation,
            this.comment,
            this.annotationParent
          )
          .then(function () {
            vueThis.unsavedChanges = false
            vueThis.$router.push({ name: 'tasks', params: { projectID: vueThis.projectID } })
          })
          .catch(function (error) {
            console.log(error)
          })
      }
    },
    cancel: async function () {
      if (!this.unsavedChanges) {
        this.$router.push({ name: 'tasks', params: { projectID: this.projectID } })
        return
      }
      if (
        await this.$refs.confirm.open(
          'Confirm',
          'There are unsaved changes. Are you sure you want to exit?',
          {
            okText: 'Yes',
            cancelText: 'No',
            noconfirm: false,
            color: 'error'
          }
        )
      ) {
        this.unsavedChanges = false
        this.$router.push({ name: 'tasks', params: { projectID: this.projectID } })
      }
    },
    scrollToPos: function () {
      const selection = window.getSelection()
      let top = selection.getRangeAt(0).getBoundingClientRect().top
      let height = selection.getRangeAt(0).getBoundingClientRect().height
      let preOffset = document.getElementById('file-content').offsetTop
      let winHeight = window.innerHeight

      if (top < preOffset || top > winHeight - height) {
        let to = document.getElementById('high-file-content').scrollTop - (preOffset - top)
        document.getElementById('high-file-content').scrollTo({ top: to, behavior: 'smooth' })
      }
    },
    onLink: function (text, offset_start, offset_end) {
      this.unsavedChanges = true
      let newGround = {
        text: text,
        file_id: this.selectedFile,
        offset_start: Math.min(offset_start, offset_end),
        offset_end: Math.max(offset_start, offset_end)
      }
      this.annotation_data[this.selectedRound].ground.push(newGround)
    },
    deleteRound: async function (index) {
      if (
        await this.$refs.confirm.open('Confirm', 'Are you sure?', {
          okText: 'Yes',
          cancelText: 'No',
          noconfirm: false,
          color: 'error'
        })
      ) {
        this.unsavedChanges = true
        this.removing.push(index)
        setTimeout(() => {
          if (index === this.annotation_data.length - 1) {
            if (this.annotation_data.length > 1) {
              this.selectedActorForChoice = this.annotation_data[index].speaker
            } else {
              this.selectedActorForChoice = this.actors[0].label
            }
          }
          this.annotation_data.splice(index, 1)
          this.removing = []
        }, 500)
      }
    },
    addRound: function (index) {
      this.unsavedChanges = true
      let replaceIndex = index + 1
      let s
      if (this.annotation_data.length > replaceIndex) {
        s = this.annotation_data[replaceIndex].speaker
      } else if (this.annotation_data.length > 0) {
        s = this.annotation_data[this.annotation_data.length - 1].speaker
      } else {
        // get the second one
        s = this.actors[1].label
      }
      let chosenActor = undefined
      let nextActor = undefined
      let limit = 2
      let count = 0
      let previous = undefined
      while (chosenActor === undefined) {
        count++
        if (count > limit) {
          break
        }
        for (let a of this.actors) {
          if (a.label === s && previous !== undefined) {
            chosenActor = previous
            nextActor = a.label
            break
          }
          previous = a.label
        }
      }

      if (!this.annotation_data) {
        this.annotation_data = []
      }
      if (replaceIndex === this.annotation_data.length) {
        this.selectedActorForChoice = nextActor
      }
      if (this.annotation_data.length > 0) {
        this.annotation_data.splice(replaceIndex, 0, {
          speaker: chosenActor,
          text: '',
          ground: []
        })
      } else {
        this.annotation_data = []
        this.annotation_data.push({
          speaker: chosenActor,
          text: '',
          ground: []
        })
      }
    },
    deleteGround: async function (index, gindex) {
      if (
        await this.$refs.confirm.open('Confirm', 'Are you sure?', {
          okText: 'Yes',
          cancelText: 'No',
          noconfirm: false,
          color: 'error'
        })
      ) {
        this.unsavedChanges = true
        this.annotation_data[index].ground.splice(gindex, 1)
      }
    },
    selectText: function (g) {
      if (g.file_id > 0) {
        this.selectedFile = g.file_id
        this.toBeSelected = g
        this.loadFile()
      }
      if (g.file_id < 0) {
        let message = g.name
        if (g?.link) {
          let a = document.createElement('a')
          a.href = g.link
          a.target = '_blank'
          a.textContent = g.link
          message += '<br />' + a.outerHTML
        }
        message += '<br />' + g.text
        this.$refs.confirm.open('Ground info', message, {
          noconfirm: true,
          okText: 'Ok',
          color: 'primary'
        })
      }
    },
    loadSelection: function () {
      let vueThis = this
      nextTick().then(function () {
        if (vueThis.toBeSelected !== undefined) {
          // https://stackoverflow.com/questions/17675056/set-selection-by-range-in-javascript
          // https://developer.mozilla.org/en-US/docs/Web/API/Range/setStart
          var selection = window.getSelection()
          var range = document.createRange()
          let referenceNode = document.getElementById('file-content').childNodes[0]
          range.setStart(referenceNode, vueThis.toBeSelected.offset_start)
          range.setEnd(referenceNode, vueThis.toBeSelected.offset_end)
          selection.removeAllRanges()
          selection.addRange(range)
          vueThis.scrollToPos()

          vueThis.toBeSelected = undefined
        }
      })
    },
    loadFile: function () {
      if (this.selectedFile > 0) {
        if (this.selectedFile in this.fileContentBuffer) {
          this.fileContent = this.fileContentBuffer[this.selectedFile]
          this.loadSelection()
        } else {
          let vueThis = this
          this.loadingFile = true
          dataService
            .getFileContent(this.projectID, this.selectedFile)
            .then(function (data) {
              vueThis.fileContentBuffer[vueThis.selectedFile] = data.data
              vueThis.fileContent = vueThis.fileContentBuffer[vueThis.selectedFile]
              vueThis.loadingFile = false
              vueThis.loadSelection()
            })
            .catch(function () {
              vueThis.loadingFile = false
            })
        }
      }
    }
  }
}
</script>

<template>
  <splitpanes class="default-theme">
    <pane min-size="20" class="file-pane" size="35">
      <ConfirmDialog ref="confirm"></ConfirmDialog>
      <!--      <DialogGeneric-->
      <!--        v-model="showChoiceDialog"-->
      <!--        component-file="./dialog-dialogue.vue"-->
      <!--        :data="{-->
      <!--          speaker:-->
      <!--            useGroundForChoice.length > 0-->
      <!--              ? annotation_data[annotation_data.length - 1].speaker-->
      <!--              : selectedActorForChoice,-->
      <!--          taskInfo: taskInfo,-->
      <!--          fileContentBuffer: fileContentBuffer,-->
      <!--          projectID: Number(projectID),-->
      <!--          annotation_data: annotation_data,-->
      <!--          useGroundForChoice: useGroundForChoice-->
      <!--        }"-->
      <!--        @refresh="addByChoice"-->
      <!--      ></DialogGeneric>-->
      <v-row>
        <v-col>
          <p class="ma-2 text-center" id="files-p">
            <v-icon icon="mdi-database-outline me-2"></v-icon>
            <span class="font-weight-bold">Data sources</span>
          </p>
        </v-col>
      </v-row>
      <v-select
        :items="filesForSelect"
        :item-props="true"
        v-model="selectedFile"
        @update:model-value="loadFile"
      ></v-select>
      <highlightable
        :disabled="!actorsWithGround.has(annotation_data[selectedRound]?.speaker)"
        v-if="selectedFile > 0 && !loadingFile"
        @link="onLink"
        id="high-file-content"
      >
        <pre id="file-content">{{ fileContent }}</pre>
      </highlightable>
      <v-skeleton-loader id="file-loader" type="paragraph" v-if="loadingFile"></v-skeleton-loader>
      <div v-if="selectedFile <= 0 || loadingFile" class="empty-div">
        <div v-if="selectedFile === -1">
          <h3 class="mb-3">External ground</h3>
          <v-text-field label="Document name" required v-model="externalGround.name" />
          <v-text-field label="External link" v-model="externalGround.link" />
          <v-textarea label="Text" rows="2" v-model="externalGround.text" auto-grow></v-textarea>
          <div class="text-right">
            <DynamicButton
              text="Confirm"
              :color="
                actorsWithGround.has(annotation_data[selectedRound]?.speaker) ? 'white' : 'red'
              "
              :disabled="
                !actorsWithGround.has(annotation_data[selectedRound]?.speaker) ||
                !externalGround.name ||
                !externalGround.text.trim().length
              "
              icon="mdi-file-document-plus-outline"
              @click.stop="addExternalGround"
              class="ms-3"
            ></DynamicButton>
          </div>
        </div>
      </div>
    </pane>
    <pane class="dialogue-pane">
      <v-container fluid id="dialogue-div" v-if="!loadingData">
        <v-row>
          <v-col cols="7" xl="8">
            <p class="ma-2 text-center">
              <v-icon icon="mdi-forum-outline me-2"></v-icon>
              <span class="font-weight-bold">Dialogue</span>
            </p>
          </v-col>
          <v-divider vertical></v-divider>
          <v-col cols="5" xl="4">
            <p class="ma-2 text-center">
              <v-icon icon="mdi-file-document-outline me-2"></v-icon>
              <span class="font-weight-bold">Ground text spans</span>
            </p>
          </v-col>
        </v-row>
        <v-row v-if="Object.keys(annotation_data).length === 0" class="ma-3">
          <v-col class="text-center" :class="{ 'v-col-4': taskInfo.inside_type === 'choice' }">
            <v-btn
              prepend-icon="mdi-plus"
              class="ma-1"
              @click="addRound(-1)"
              text="Start empty"
              :disabled="this.showChoiceDialog"
            >
            </v-btn>
          </v-col>

          <template v-if="taskInfo.inside_type === 'choice'">
            <v-col class="text-center">
              <v-select
                :items="rolesForSelect"
                :item-props="true"
                v-model="selectedActorForChoice"
                :disabled="this.showChoiceDialog"
              >
              </v-select>
            </v-col>
            <v-col class="text-center">
              <v-btn
                class="ma-1"
                prepend-icon="mdi-auto-fix"
                text="Add dynamic turn"
                @click="callDynamic"
                :disabled="this.showChoiceDialog"
              />
            </v-col>
          </template>
        </v-row>
        <v-row
          v-for="(round, index) in annotation_data"
          :key="index"
          :class="{
            'selected-row': selectedRound === index,
            removing: removing.includes(index)
            // 'forbidden-ground': !actorsWithGround.has(annotation_data[index]?.speaker)
          }"
          @click="selectedRound = index"
        >
          <v-col cols="7" xl="8">
            <v-row>
              <v-col>
                <v-select
                  :items="rolesForSelect"
                  :item-props="true"
                  v-model="round['speaker']"
                  @update:modelValue="unsavedChanges = true"
                  :disabled="this.showChoiceDialog"
                >
                  <template #prepend>
                    <v-btn
                      icon=""
                      class="ma-1"
                      @click="addRound(index - 1)"
                      :disabled="this.showChoiceDialog"
                    >
                      <v-icon class="icon-up"></v-icon>
                    </v-btn>
                    <v-btn
                      icon=""
                      class="ma-1"
                      @click="addRound(index)"
                      :disabled="this.showChoiceDialog"
                    >
                      <v-icon class="icon-down"></v-icon>
                    </v-btn>
                    <v-btn
                      v-if="taskInfo.inside_type === 'choice' && index === annotation_data.length - 1"
                      class="ma-1"
                      icon="mdi-auto-fix"
                      @click="callDynamic"
                      :disabled="this.showChoiceDialog"
                    />
                  </template>
                  <template #append>
                    <v-btn
                      color="red"
                      class="ma-1"
                      icon="mdi-trash-can-outline"
                      @click="deleteRound(index)"
                      :disabled="this.showChoiceDialog"
                    />
                  </template>
                </v-select>
                <v-textarea
                  rows="1"
                  v-model="round['text']"
                  @focus="selectedRound = index"
                  @keyup="unsavedChanges = true"
                  auto-grow
                  hide-details="auto"
                  :disabled="this.showChoiceDialog"
                ></v-textarea>
              </v-col>
            </v-row>
          </v-col>
          <v-divider vertical></v-divider>
          <v-col cols="5" xl="4">
            <v-icon
              v-if="
                round.ground.length === 0 && !actorsWithGround.has(annotation_data[index]?.speaker)
              "
              icon="mdi-file-document-remove-outline"
              color="red"
              class="opacity-50"
              size="x-large"
            ></v-icon>
            <v-card v-if="round.ground.length > 0">
              <v-list class="ground-list">
                <template v-for="(g, gindex) in round.ground" :key="gindex">
                  <v-list-item
                    :title="g.file_id > 0 ? files[g.file_id].name : g.name"
                    :subtitle="g.text"
                    @click="selectText(g)"
                  >
                    <template v-slot:append>
                      <v-btn
                        color="red"
                        icon="mdi-trash-can-outline"
                        variant="text"
                        @click.stop="deleteGround(index, gindex)"
                      ></v-btn>
                    </template>
                    <template v-slot:prepend>
                      <v-icon
                        v-if="g.file_id > 0"
                        color="black"
                        icon="mdi-file-document-outline"
                        size="x-small"
                      ></v-icon>
                      <template v-if="g.file_id < 0">
                        <a v-if="g?.link" :href="g.link" target="_blank">
                          <v-icon icon="mdi-open-in-new" color="black" size="x-small"></v-icon>
                        </a>
                        <v-icon
                          v-else
                          icon="mdi-open-in-new"
                          class="opacity-50"
                          size="x-small"
                        ></v-icon>
                      </template>
                    </template>
                  </v-list-item>
                </template>
              </v-list>
            </v-card>
            <v-btn
              v-if="shouldAddFromGround(index)"
              text="Add from ground"
              prepend-icon="mdi-auto-fix"
              class="mt-3"
              @click="callDynamicWithGround"
            ></v-btn>
          </v-col>
        </v-row>
        <!--        <v-row v-if="taskInfo.inside_type === 'choice'" id="dynamic-turn">-->
        <!--          <v-col>-->
        <!--            <v-select-->
        <!--              :items="rolesForSelect"-->
        <!--              :item-props="true"-->
        <!--              v-model="selectedActorForChoice"-->
        <!--              :disabled="this.showChoiceDialog"-->
        <!--            >-->
        <!--              <template #append>-->
        <!--                <v-btn-->
        <!--                  class="ma-1"-->
        <!--                  prepend-icon="mdi-auto-fix"-->
        <!--                  text="Add dynamic turn"-->
        <!--                  @click="callDynamic"-->
        <!--                  :disabled="this.showChoiceDialog"-->
        <!--                />-->
        <!--              </template>-->
        <!--            </v-select>-->
        <!--          </v-col>-->
        <!--        </v-row>-->
        <v-row v-if="showChoiceDialog">
          <v-col>
            <DialogDialogue
              v-bind="{
                speaker:
                  useGroundForChoice.length > 0
                    ? annotation_data[annotation_data.length - 1].speaker
                    : selectedActorForChoice,
                taskInfo: taskInfo,
                fileContentBuffer: fileContentBuffer,
                projectID: Number(projectID),
                annotation_data: annotation_data,
                useGroundForChoice: useGroundForChoice
              }"
              @exit="showChoiceDialog = false"
              @refresh="addByChoice"
            ></DialogDialogue>
          </v-col>
        </v-row>
        <div class="bg-primary" id="buttons-container">
          <v-expand-transition>
            <v-textarea
              v-show="commentVisible"
              label="Comment"
              bg-color="white"
              v-model="comment"
              @keyup="unsavedChanges = true"
              auto-grow
              rows="2"
            ></v-textarea>
          </v-expand-transition>
          <DynamicButton
            text="Show comment"
            color="white"
            icon="mdi-comment-edit"
            @click.stop="commentVisible = !commentVisible"
            class="ms-3"
          ></DynamicButton>
          <DynamicButton
            text="Save and close"
            color="white"
            icon="mdi-check"
            @click.stop="confirmAnnotation"
            class="ms-3"
          ></DynamicButton>
          <DynamicButton
            text="Discard changes"
            color="white"
            icon="mdi-close"
            @click.stop="cancel"
            class="ms-3"
          ></DynamicButton>
        </div>
      </v-container>
    </pane>
  </splitpanes>
</template>

<style>
.ground-list .v-list-item__prepend > .v-icon ~ .v-list-item__spacer,
.ground-list .v-list-item__prepend > a ~ .v-list-item__spacer {
  width: 10px;
}

.removing {
  animation-name: removing;
  animation-duration: 500ms;
  animation-iteration-count: 1;
  overflow: hidden;
}

@keyframes removing {
  from {
    height: 180px;
  }
  to {
    height: 0;
  }
}

#buttons-container {
  position: sticky;
  bottom: 0;
  padding: 20px;
  text-align: right;
  margin-top: 20px;
}

.icon-up {
  background-image: url('/plus_up.svg');
}

.icon-down {
  background-image: url('/plus_down.svg');
}

.selected-row {
  background-color: #ddf;
  position: relative;
}

.selected-row.forbidden-ground {
  background-color: #fdd;
}

.ground-list .v-list-item-title {
  font-size: 0.8em;
}

#file-content {
  white-space: pre-wrap; /* Since CSS 2.1 */
  word-wrap: break-word; /* Internet Explorer 5.5+ */
}

.file-pane {
  display: flex;
  flex-direction: column;
  padding: 10px;
}

.dialogue-pane {
  padding: 10px 0 0 0;
}

.empty-div {
  height: 100%;
  flex: 1 1 auto;
  overflow: auto;
}

#high-file-content {
  flex: 1 1 auto;
  overflow: auto;
  height: 100%;
}

#dialogue-div {
  overflow: auto;
  height: 100%;
  padding: 0;
}

#dialogue-div > .v-row {
  border-bottom: 1px solid black;
  margin-left: 0;
  margin-right: 0;
}

#dialogue-div > .v-row:nth-last-child(2),
#dialogue-div > .v-row#dynamic-turn {
  border-bottom: none;
}

#files-p {
  padding-bottom: 12px;
}
</style>
