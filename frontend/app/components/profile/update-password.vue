<template>
  <CrudPage
    :config="{
      entityNamePlural: 'Update Password',
      entityName: 'Update Password',
      canRead: true,
      canEdit: false,
      canDelete: false,
      canCreate: false,
    }"
  >
    <template #content>
      <UProgress :class="[loading ? 'visible' : 'invisible', 'mb-1']" />
      <CrudForm
        ref="form"
        :api="api"
        :config="config"
        :entity="entity"
        @submit="
          entity = { password: '', old_password: '' };
          valid = false;
        "
        @validation-change="(isValid) => (valid = isValid)"
        @new-loading="(newLoading) => (loading = newLoading)"
        @error="
          (error) => {
            if (error?.statusCode === 401) {
              toast.add({
                title: 'Error',
                description: 'Invalid current password',
                color: 'error',
              });
            }
          }
        "
      />
      <div class="mt-8 flex justify-end">
        <UButton
          :disabled="!valid"
          :loading="loading"
          label="Update Password"
          @click="
            loading = true;
            form.submit();
          "
        />
      </div>
    </template>
  </CrudPage>
</template>

<script setup lang="ts">
import * as z from "zod";

const api = useApi("/api/profile/update-password/");
const validation = useValidation();
const toast = useToast();
const form = ref();
const valid = ref(false);
const loading = ref(false);
const entity = ref({ password: "", old_password: "" });
const config = ref({
  entityName: "Password",
  editFormFields: [
    {
      key: "old_password",
      label: "Password",
      type: "password",
      placeholder: "Enter your current password",
      required: true,
      size: "xl",
      icon: "i-lucide-key",
    },
    {
      key: "password",
      label: "New password",
      type: "password",
      placeholder: "Enter your new password",
      required: true,
      size: "xl",
      icon: "i-lucide-key-round",
    },
    {
      key: "confirmpassword",
      label: "Confirm password",
      type: "password",
      placeholder: "Repeat your new password",
      required: true,
      size: "xl",
      icon: "i-lucide-key-round",
    },
  ],
  editFormSchema: z
    .object({
      old_password: validation.secret("password", true, 200),
      password: validation.passwordPolicy,
      confirmpassword: z.string("Password must be confirmed"),
    })
    .refine((data) => data.password === data.confirmpassword, {
      message: "Passwords don't match",
      path: ["confirmpassword"],
    })
    .refine((data) => data.password !== data.old_password, {
      message: "New and current passwords are equal",
      path: ["password"],
    }),
  putEndpoint: () => "/api/profile/update-password/",
});
</script>
