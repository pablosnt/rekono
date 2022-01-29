<template>
  <div id="public-page" class="fixed-top d-flex align-items-center justify-content-center" style="bottom: 0">
    <b-card id="public-form" img-src="/static/logo-black.png" img-top img-height="150" class="mb-3">
      <slot/>
    </b-card>
  </div>
</template>

<style>
#public-page {
  height: 100%;
  background-image: url('/static/background.jpg');
  background-size: cover;
}
#public-form {
  background: white;
}
</style>