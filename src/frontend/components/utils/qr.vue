<template>
  <div ref="qrCode" />
</template>
<!-- CODE: Move all utils to base? -->

<script setup lang="ts">
import QRCodeStyling from "qr-code-styling";

const props = defineProps({
  data: String,
});
const qrCode = ref(null);
const options = {
  width: 250,
  type: "svg",
  data: props.data,
  image: "/favicon.png",
  dotsOptions: {
    color: "#cb001d",
    type: "rounded",
  },
  backgroundOptions: {
    color: "white",
  },
  cornersDotOptions: {
    color: "black",
    type: "square",
  },
  cornersSquareOptions: {
    color: "black",
    type: "extra-rounded",
  },
  imageOptions: {
    hideBackgroundDots: true,
    imageSize: 0.4,
    margin: 0,
  },
};
const qr = new QRCodeStyling(options);

onMounted(() => {
  qr.append(qrCode.value);
});
watch(
  () => props.data,
  (newValue: string) => {
    options.data = newValue;
    qr.update(options);
  },
);
</script>
