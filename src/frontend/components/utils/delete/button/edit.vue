<template>
  <v-speed-dial transition="scale-transition" location="bottom end">
    <template #activator="{ props: activatorProps }">
      <v-btn
        v-bind="activatorProps"
        variant="text"
        size="large"
        color="grey"
        icon="mdi-cog"
        @click.prevent.stop
      />
    </template>
    <v-dialog width="auto">
      <template #activator="{ props: activatorProps }">
        <v-btn
          key="1"
          icon="mdi-pencil"
          color="black"
          v-bind="activatorProps"
        />
      </template>
      <template #default="{ isActive }">
        <slot name="edit-dialog" :is-active="isActive" />
      </template>
    </v-dialog>
    <v-dialog width="500" class="overflow-auto">
      <template #activator="{ props: activatorProps }">
        <v-btn
          key="2"
          icon="mdi-trash-can-outline"
          color="red"
          v-bind="activatorProps"
        />
      </template>
      <template #default="{ isActive }">
        <slot name="delete-dialog" :is-active="isActive" />
      </template>
    </v-dialog>
  </v-speed-dial>
</template>
