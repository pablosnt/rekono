<template>
  <BaseDialog
    title="Defect-Dojo Sync"
    width="1000"
    :avatar="integration.icon"
    :loading="loading"
    @close-dialog="
      loading = false;
      $emit('close-dialog');
    "
  >
    <p>You can create new entities in Defect-Dojo or choose existing ones</p>
    <v-stepper v-model="step" alt-labels flat>
      <v-stepper-header>
        <v-stepper-item title="Product type" :value="1" />
        <v-divider />
        <v-stepper-item title="Product" :value="2" />
        <v-divider />
        <v-stepper-item title="Engagement" subtitle="Optional" :value="3" />
      </v-stepper-header>
      <v-stepper-window>
        <v-container fluid>
          <v-row v-if="step === 1" justify="space-between" align="center">
            <v-col cols="4">
              <VNumberInput
                v-model="productType"
                control-variant="split"
                label="Product type ID"
                inset
                clearable
                variant="outlined"
                :max="999999999"
                :min="1"
                @update:model-value="ptDisabled = productType ? true : false"
              />
            </v-col>
            <v-divider vertical />
            <v-col cols="7">
              <ProjectDefectDojoForm
                :api="useApi('/api/defect-dojo/product-types/')"
                :disabled="ptDisabled"
                @loading="(value) => (loading = value)"
                @completed="
                  (data) => {
                    productType = data.id;
                    step++;
                  }
                "
              />
            </v-col>
          </v-row>

          <v-row v-if="step === 2" justify="space-between" align="center">
            <v-col cols="4">
              <VNumberInput
                v-model="product"
                control-variant="split"
                label="Product ID"
                inset
                clearable
                variant="outlined"
                :max="999999999"
                :min="1"
                @update:model-value="pDisabled = product ? true : false"
              />
            </v-col>
            <v-divider vertical />
            <v-col cols="7">
              <ProjectDefectDojoForm
                :api="useApi('/api/defect-dojo/products/')"
                :extra-data="{
                  product_type: productType,
                  project_id: project.id,
                }"
                :disabled="pDisabled"
                @loading="(value) => (loading = value)"
                @completed="
                  (data) => {
                    product = data.id;
                    step++;
                  }
                "
              />
            </v-col>
          </v-row>

          <v-row v-if="step === 3" justify="center" align="center">
            <v-col cols="10">
              <v-alert
                class="text-center"
                color="info"
                icon="$info"
                variant="tonal"
                text="Leave blank to automatically create a new engagement for each target"
            /></v-col>
          </v-row>
          <v-row v-if="step === 3" justify="space-between" align="center">
            <v-col cols="4">
              <VNumberInput
                v-model="engagement"
                control-variant="split"
                label="Engagement ID"
                inset
                clearable
                variant="outlined"
                :max="999999999"
                :min="1"
                @update:model-value="eDisabled = engagement ? true : false"
              />
            </v-col>
            <v-divider vertical />
            <v-col cols="7">
              <ProjectDefectDojoForm
                :api="useApi('/api/defect-dojo/engagements/')"
                :extra-data="{ product: product }"
                :disabled="eDisabled"
                @loading="(value) => (loading = value)"
                @completed="
                  (data) => {
                    engagement = data.id;
                    submit();
                  }
                "
              />
            </v-col>
          </v-row>
        </v-container>
      </v-stepper-window>
      <template #actions>
        <v-stepper-actions
          v-if="step < 3"
          color="blue"
          :disabled="
            (step === 1 && !productType) || (step === 2 && !product)
              ? true
              : 'prev'
          "
          @click:next="step++"
          @click:prev="step--"
        />
      </template>
    </v-stepper>
    <UtilsSubmit
      v-if="step == 3"
      text="Enable Sync"
      color="blue"
      @click="submit()"
    />
  </BaseDialog>
</template>

<script setup lang="ts">
import { VNumberInput } from "vuetify/labs/VNumberInput";
const props = defineProps({
  api: Object,
  project: Object,
  integration: Object,
});
const emit = defineEmits(["close-dialog", "completed"]);

const productType = ref(null);
const ptDisabled = ref(false);
const product = ref(null);
const pDisabled = ref(false);
const engagement = ref(null);
const eDisabled = ref(false);
const loading = ref(false);
const step = ref(1);

function submit(): void {
  if (productType.value && product.value) {
    loading.value = true;
    props.api
      .create({
        project: props.project.id,
        product_type_id: productType.value,
        product_id: product.value,
        engagement_id: engagement.value,
      })
      .then((response) => {
        emit("completed", response);
        loading.value = false;
      })
      .catch(() => (loading.value = false));
  }
}
</script>
