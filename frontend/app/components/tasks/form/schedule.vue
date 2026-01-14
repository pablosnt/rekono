<template>
  <div class="space-y-4 mx-auto mt-3">
    <UFormField
      label="Datetime"
      hint="Schedule the execution start"
      class="text-center"
    >
      <UInputDate
        ref="inputDate"
        v-model="scheduledAt"
        class="w-100"
        :min-value="now(getLocalTimeZone())"
        size="xl"
        variant="outline"
        :hour-cycle="24"
        granularity="minute"
        @update:model-value="
          (datetime) => {
            $emit('update-scheduled-at', datetime);
            if (!scheduledDate) {
              scheduledDate = today(getLocalTimeZone());
            }
            if (datetime.year) {
              scheduledDate.year = datetime.year;
            }
            if (datetime.month) {
              scheduledDate.month = datetime.month;
            }
            if (datetime.day) {
              scheduledDate.day = datetime.day;
            }
          }
        "
      >
        <template #leading>
          <UPopover :reference="inputDate?.inputsRef[3]?.$el">
            <UButton
              color="neutral"
              variant="link"
              icon="i-lucide-calendar"
              aria-label="Select a date"
              class="px-0"
            />
            <template #content>
              <UCalendar
                v-model="scheduledDate"
                class="p-2"
                :min-value="today(getLocalTimeZone())"
                @update:model-value="
                  (date) => {
                    if (
                      scheduledAt &&
                      scheduledAt.year === date.year &&
                      scheduledAt.month === date.month &&
                      scheduledAt.day === date.day
                    ) {
                      return;
                    }
                    const tz = getLocalTimeZone();
                    scheduledAt = now(tz);
                    scheduledAt.year = date.year;
                    scheduledAt.month = date.month;
                    scheduledAt.day = date.day;
                    const _today = now(tz);
                    if (
                      scheduledAt.year === _today.year &&
                      scheduledAt.month === _today.month &&
                      scheduledAt.day === _today.day &&
                      scheduledAt.hour === _today.hour
                    ) {
                      scheduledAt = scheduledAt.add({ hours: 1 });
                    }
                    $emit('update-scheduled-at', scheduledAt);
                  }
                "
              />
            </template>
          </UPopover>
        </template>
        <template v-if="scheduledAt" #trailing>
          <UButton
            color="neutral"
            variant="link"
            icon="i-lucide-x"
            aria-label="Clear selected date"
            @click="
              scheduledAt = undefined;
              scheduledDate = undefined;
              $emit('update-scheduled-at', scheduledAt);
            "
          />
        </template>
      </UInputDate>
    </UFormField>
    <UAlert title="Monitor" color="neutral" class="mt-8">
      <template #leading>
        <USwitch
          v-model="monitor"
          @update:model-value="
            (value) => {
              repeatIn = value ? 1 : undefined;
              repeatTimeUnit = value ? 'Days' : undefined;
              $emit('update-repeat-in', repeatIn);
              $emit('update-repeat-time-unit', repeatTimeUnit);
            }
          "
        />
      </template>
      <template v-if="repeatIn" #description>
        <div class="flex items-center gap-2">
          <span>Run this scan each</span
          ><UInput
            v-model="repeatIn"
            type="number"
            min="1"
            class="w-20"
            @update:model-value="$emit('update-repeat-in', repeatIn)"
          />
          <USelect
            v-model="repeatTimeUnit"
            :items="utils.timeUnitOptions"
            class="w-32"
            @update:model-value="
              $emit('update-repeat-time-unit', repeatTimeUnit)
            "
          />
        </div>
      </template>
    </UAlert>
  </div>
</template>

<script setup lang="ts">
import type { ZonedDateTime } from "@internationalized/date";
import { today, now, getLocalTimeZone } from "@internationalized/date";

defineEmits<{
  "update-scheduled-at": [newScheduledAt: ZonedDateTime | undefined];
  "update-repeat-in": [newRepeatIn: number | undefined];
  "update-repeat-time-unit": [newRepeatTimeUnit: string];
}>();

const utils = useUtils();
const inputDate = useTemplateRef("inputDate");
const scheduledDate = ref();
const scheduledAt = ref();
const monitor = ref(false);
const repeatIn = ref();
const repeatTimeUnit = ref("Days");
</script>
