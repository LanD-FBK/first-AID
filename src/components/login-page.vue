<script>
import dataService from './dataService'
import { useLoginStore } from '@/store'

export default {
  data() {
    return {
      ds: dataService,
      loginStore: useLoginStore(),
      username: '',
      password: '',
      goodLogin: false,
      regole: [
        function (value) {
          if (value) return true
          return 'This field cannot be empty'
        }
      ],
      snackbar: false,
      loading: false
    }
  },
  mounted: function () {
    if (localStorage.getItem('token')) {
      //Tries to load projects with stored token. If '401' goes back to 'login'
      //TODO: go to login
    }
  },
  methods: {
    submit: function () {
      const self = this
      this.loading = true
      dataService
        .getToken(this.username, this.password)
        .then(function (data) {
          self.loginStore.updateBearer(data.data.access_token)
          self.loginStore.updateUsername(self.username)
          self.loading = false
          self.$router.push({ name: 'projects' })
        })
        .catch(function (error) {
          console.log('in catch')
          console.log(error)
          self.snackbar = true
          self.loading = false
        })
    }
  },
  computed: {
    isButtonDisabled() {
      //Bitwise AND is used to avoid short-circuiting and always evaluate both conditions
      return Boolean(this.username) & Boolean(this.password) ? false : true
    }
  }
}
</script>

<template>
  <v-container class="fill-height" align="center">
    <v-row>
      <v-col>
        <!-- Login handling: if successful, button becomes a spinner and waits for auth. If successful, redirects to 'projects'-->
        <v-sheet class="mx-6" width="300px">
          <div class="text-h4 py-4">Login</div>
          <v-form @submit.prevent="submit" v-model="goodLogin">
            <v-text-field label="Username" v-model="username" :rules="regole"></v-text-field>
            <!-- 'type' is 'password' in order to show **** instead of abcd-->
            <v-text-field
              label="Password"
              v-model="password"
              type="password"
              :rules="regole"
            ></v-text-field>
            <v-btn type="submit" class="ma-2" :loading="loading" :disabled="isButtonDisabled"
              >Login</v-btn
            >
          </v-form>
        </v-sheet>

        <v-snackbar v-model="snackbar" timeout="3000">
          Wrong Username or Password!

          <template v-slot:actions>
            <v-btn color="red" variant="text" @click="snackbar = false"> Close </v-btn>
          </template>
        </v-snackbar>
      </v-col>
    </v-row>
  </v-container>
</template>
