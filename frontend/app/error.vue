<template>
  <UApp>
    <PublicPage>
      <PublicForm :title="title" :description="description">
        <template #footer>
          <UButton
            :label="label"
            :icon="icon"
            color="primary"
            size="xl"
            @click="
              clearError({
                redirect: userStore.is_authenticated ? '/' : '/login',
              })
            "
          />
        </template>
      </PublicForm>
    </PublicPage>
  </UApp>
</template>

<script setup lang="ts">
import { useUserStore } from "~/store/user";

const props = defineProps<{
  error: { statusCode?: number };
}>();

const title = ref(`HTTP ${props.error.statusCode} error`);
const description = ref(
  "Something broke on our end while handling your request. Try again in some minutes",
);
switch (props.error.statusCode) {
  case 403:
    title.value = "Access denied";
    description.value = "You don't have permission to view this page";
    break;
  case 404:
    title.value = "Page not found";
    description.value =
      "The page you're looking for doesn't exist or has been moved. Go back home to keep going";
    break;
  case 500:
    title.value = "Something went wrong";
    break;
}
const userStore = useUserStore();
const label = ref("Sign in");
const icon = ref("i-lucide-log-in");
if (userStore.is_authenticated) {
  label.value = "Back to home";
  icon.value = "i-lucide-house";
}
</script>
