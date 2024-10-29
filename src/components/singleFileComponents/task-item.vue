<script>
export default{
    props: {
      title: String,
        taskID: Number,
        projectID: Number,
        isActive: Boolean
    }
}
</script>

<template>
     <v-container fluid>
    <v-row>
      <v-col cols="12">
        <v-card @click.prevent="this.$router.push({
                      name: 'annotation',
                      params: { projectID: this.projectID , taskID: this.taskID }
                    })">
          <v-row align="center">
            <v-col cols="12" sm="3" md="6" xl="6" xs="6">
              <v-row class="d-flex justify-left">
                <v-col>
                  <v-card-title>{{ title }}</v-card-title>
                  <v-card-subtitle>Task ID: {{ taskID }}. Task {{ isActive ? 'Active' : 'not Active' }}</v-card-subtitle>
                </v-col>
              </v-row>
            </v-col>
            <v-col cols="12" lg="6" sm="9" md="6" xl="6" xs="6">
              <v-card-actions>
                <v-btn title="Go To Task"/>
              </v-card-actions>
            </v-col>
          </v-row>
        </v-card>
      </v-col>
    </v-row>
     </v-container>
</template>