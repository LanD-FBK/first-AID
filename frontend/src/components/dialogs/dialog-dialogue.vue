<script>
import dataService from '@/components/dataService.js'
import axios from 'axios'

export default {
  name: 'dialog-dialogue',
  props: [
    'speaker',
    'taskInfo',
    'fileContentBuffer',
    'projectID',
    'annotation_data',
    'useGroundForChoice'
  ],
  emit: ['exit', 'refresh'],
  data() {
    return {
      options: [],
      loadedOptions: false,
      selectedOption: null,
      speakerName: null
    }
  },
  methods: {
    scrollToBottom: function() {
      const element = document.getElementById("dialogue-div")
      element.scrollTop = element.scrollHeight
    },
    confirmChoice: function () {
      this.$emit('refresh', this.options[this.selectedOption])
    },
    loadChoices: function () {
      let vueThis = this
      vueThis.loadedOptions = false

      let optionNumber = 0
      for (let s of this.taskInfo.actors) {
        if (s.label === this.speaker) {
          optionNumber = s.answers
          vueThis.speakerName = s.name
        }
      }

      let documents = []
      let documentIndexes = []

      for (let file_id in this.fileContentBuffer) {
        documentIndexes.push(Number(file_id))
        documents.push(this.fileContentBuffer[file_id])
      }

      let dialogue = []
      let maxIndex = this.annotation_data.length - 1
      if (this.useGroundForChoice.length > 0) {
        maxIndex = this.annotation_data.length - 2
      }
      for (let index = 0; index <= maxIndex; index++) {
        let turn = this.annotation_data[index]
        dialogue.push({
          speaker: turn.speaker,
          turn_text: turn.text
        })
      }
      let config = {};
      if (this.taskInfo['meta']['inside_type_header_key']) {
        config['headers'] = {};
        config['headers'][this.taskInfo['meta']['inside_type_header_key']] = this.taskInfo['meta']['inside_type_header_value'];
      }
      let d = {
        generation_mode: this.taskInfo['meta']['inside_type_api'],
        documents: documents,
        dialogue: dialogue,
        speaker: this.speaker,
        options_number: optionNumber,
        manual_selected_grounds: this.useGroundForChoice
      }

      axios.post(this.taskInfo['meta']['inside_type_endpoint'], d, config).then((response) => {
        vueThis.options = []
        for (let o of response.data) {
          for (let g of o.ground) {
            g.file_id = documentIndexes[g.file_index]
            delete g.file_index
          }
          vueThis.options.push(o)
        }
        vueThis.loadedOptions = true
        vueThis.$nextTick(function () {
          vueThis.scrollToBottom()
        })
      }).catch(() => {
        alert("Error in retrieving dialogue")
        vueThis.$emit('exit')
      })
    }
  },
  mounted: function () {
    this.scrollToBottom()

    let vueThis = this
    let promises = []
    let fileIDs = []
    for (let file of this.taskInfo.files) {
      if (!(file.file_id in this.fileContentBuffer)) {
        promises.push(dataService.getFileContent(this.projectID, file.file_id))
        fileIDs.push(file.file_id)
      }
    }
    if (promises.length > 0) {
      Promise.all(promises).then(function (result) {
        for (let i = 0; i < result.length; i++) {
          vueThis.fileContentBuffer[fileIDs[i]] = result[i].data
        }
        vueThis.loadChoices()
      })
    } else {
      this.loadChoices()
    }
  }
}
</script>

<template>
  <v-card title="Select dialogue turn" prepend-icon="mdi-message-outline">
    <v-card-text>
      <v-row>
        <v-col cols="12" class="text-center" v-if="!loadedOptions">
          <v-progress-circular indeterminate class="mx-auto" :size="128"></v-progress-circular>
        </v-col>
        <v-col v-else>
          <p class="mb-3">
            Speaker:
            <v-chip>{{ speakerName }}</v-chip>
          </p>
          <v-card>
            <v-tabs v-model="selectedOption" bg-color="primary">
              <v-tab v-for="(option, index) of options" :key="'option_' + index" :value="index"
                >Option
                {{ index + 1 }}
              </v-tab>
            </v-tabs>
            <v-card-text>
              <v-tabs-window v-model="selectedOption">
                <v-tabs-window-item
                  v-for="(option, index) of options"
                  :key="'option_' + index"
                  :value="index"
                >
                  <p>{{ option['turn_text'] }}</p>
                  <template v-if="option['ground'].length > 0">
                    <p class="mt-3"><strong>Ground</strong></p>
                    <p v-for="(g, index) in option['ground']" :key="index">{{ g['text'] }}</p>
                  </template>
                </v-tabs-window-item>
              </v-tabs-window>
            </v-card-text>
          </v-card>
          <div class="text-center mt-4">
            <v-btn
              color="primary"
              text="Pick this"
              prepend-icon="mdi-check"
              @click="confirmChoice"
            ></v-btn>
            <v-btn
              color="yellow"
              class="ms-3"
              text="Regenerate options"
              prepend-icon="mdi-reload"
              @click="loadChoices"
            ></v-btn>
            <v-btn
              color="red"
              class="ms-3"
              text="None"
              prepend-icon="mdi-close-thick"
              @click="$emit('exit')"
            ></v-btn>
          </div>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<style scoped></style>
