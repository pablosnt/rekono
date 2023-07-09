<template>
  <div id="public-page" class="fixed-top d-flex align-items-center justify-content-center mb-0">
    <b-card id="public-form" style="max-width: 30rem;" img-src="/static/logo-black.png" img-top>
      <slot/>
    </b-card>
  </div>
</template>

<style>
#public-page {
  height: 100%;
  background-image: url('/static/background.jpg');
  background-size: cover;
  background-repeat: no-repeat;
}
#public-form {
  background: white;
}
</style>