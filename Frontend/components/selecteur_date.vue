<script setup lang="ts">
import {ref} from 'vue';
import { sub, format, isSameDay, type Duration } from "date-fns";
import { DatePicker } from "v-calendar";
import "v-calendar/dist/style.css";

const emit = defineEmits(["update-range"]);

const ranges = [
  { label: "Last 7 days", duration: { days: 7 } },
  { label: "Last 14 days", duration: { days: 14 } },
  { label: "Last 30 days", duration: { days: 30 } },
  { label: "Last 3 months", duration: { months: 3 } },
  { label: "Last 6 months", duration: { months: 6 } },
  { label: "Last year", duration: { years: 1 } },
];
const selected = ref({ start: sub(new Date(), { days: 14 }), end: new Date() });

function isRangeSelected(duration: Duration) {
  return (
    isSameDay(selected.value.start, sub(new Date(), duration)) &&
    isSameDay(selected.value.end, new Date())
  );
}

function selectRange(duration: Duration) {
  const newDateFilterRange = {
    start: sub(new Date(), duration),
    end: new Date(),
  };
  selected.value = newDateFilterRange;

  // Emit event to parent component
  emit("update-range", newDateFilterRange);
}
</script>

<template>
  <UPopover :popper="{ placement: 'bottom-start' }">
    <UButton color="gray" icon="i-heroicons-calendar-days-20-solid">
      {{ format(selected.start, "d MMM, yyy") }} -
      {{ format(selected.end, "d MMM, yyy") }}
    </UButton>

    <template #panel="{ close }">
      <div
        class="flex items-center sm:divide-x divide-gray-200 dark:divide-gray-800"
      >
        <div class="hidden sm:flex flex-col py-4">
          <UButton
            v-for="(range, index) in ranges"
            :key="index"
            :label="range.label"
            color="gray"
            variant="ghost"
            class="rounded-none px-6"
            :class="[
              isRangeSelected(range.duration)
                ? 'bg-gray-100 dark:bg-gray-800'
                : 'hover:bg-gray-50 dark:hover:bg-gray-800/50',
            ]"
            truncate
            @click="selectRange(range.duration)"
          />
        </div>

        <DatePicker
          v-model="selected"
          is-range
          @close="close"
          class="bg-gray-100 dark:bg-gray-800 dark:text-white"
        />
      </div>
    </template>
  </UPopover>
</template>
