<template>
  <CrudPage
    :config="{
      entityNamePlural: 'Change Password',
      entityName: 'Change Password',
      canRead: true,
      canEdit: false,
      canDelete: false,
      canCreate: false,
    }"
  >
    <!-- TODO: This endpoint might return 401 when the old password is not correct -->
    <!-- TODO: The form must be cleared after the update -->
    <template #content>
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
    },
    {
      key: "password",
      label: "New password",
      type: "password",
      placeholder: "Enter your new password",
      required: true,
      size: "xl",
    },
    {
      key: "confirmpassword",
      label: "Confirm password",
      type: "password",
      placeholder: "Repeat your new password",
      required: true,
      size: "xl",
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
    }),
  putEndpoint: "",
});
</script>
