<template>
  <v-speed-dial transition="scale-transition" location="bottom end">
    <template #activator="{ props: activatorProps }">
      <BaseButton
        v-bind="activatorProps"
        size="large"
        color="grey"
        icon="mdi-cog"
        @click.prevent.stop
      />
    </template>
    <v-dialog key="1" width="auto">
      <template #activator="{ props: activatorProps }">
        <BaseButton
          icon="mdi-pencil"
          color="black"
          variant="flat"
          v-bind="activatorProps"
        />
      </template>
      <template #default="{ isActive }">
        <slot name="edit-dialog" :is-active="isActive" />
      </template>
    </v-dialog>
    <v-dialog key="2" width="500" class="overflow-auto">
      <template #activator="{ props: activatorProps }">
        <BaseButton
          icon="mdi-trash-can-outline"
          color="red"
          variant="flat"
          v-bind="activatorProps"
        />
      </template>
      <template #default="{ isActive }">
        <slot name="delete-dialog" :is-active="isActive" />
      </template>
    </v-dialog>
  </v-speed-dial>
</template>
