<template>
  <v-card
    elevation="4"
    :title="integration.name"
    :text="integration.description"
    :prepend-avatar="integration.icon"
    :hover="integration.id === 1 || integration.id === 4"
  >
    <template #append>
      <v-switch
        :model-value="integration.enabled"
        color="success"
        class="mt-5"
        @click="
          integrationsApi
            .update({ enabled: !integration.enabled }, integration.id)
            .then((data) => {
              integration = data;
              integration.enabled
                ? alert(
                    `${integration.name} integration has been enabled`,
                    'success',
                  )
                : alert(
                    `${integration.name} integration has been disabled`,
                    'warning',
                  );
            })
        "
      />
      <ButtonLink :link="integration.reference" />
    </template>
  </v-card>
</template>

<script setup lang="ts">
defineProps({
  api: Object,
  integration: Object,
});
const alert = ref(useAlert());
</script>
