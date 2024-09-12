<template>
  <MenuProject>
    <TabTarget>
      <v-container fluid>
        <v-row justify="center" dense>
          <v-col cols="10">
            <v-alert
              class="text-center"
              color="info"
              icon="$info"
              variant="tonal"
              text="These parameters can be defined to provide already known information or issues about the target. They will be used as a tool input only when this kind of information can't be provided automatically from the previous results. You can also use these parameters to provide the needed inputs to run some tools outside of a process. For example, you can define some CVEs, and then run SearchSploit to find their known exploits."
            />
          </v-col>
        </v-row>
        <v-row justify="center" dense>
          <v-col cols="10">
            <ParametersTechnology />
          </v-col>
        </v-row>
        <v-row justify="center" dense>
          <v-col cols="10">
            <ParametersVulnerability />
          </v-col>
        </v-row>
      </v-container>
    </TabTarget>
  </MenuProject>
</template>

<script setup lang="ts">
definePageMeta({ layout: false });
</script>
