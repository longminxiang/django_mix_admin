(function ($) {
  var BindingWechat = Vue.component('BindingWechat', {
    template: '<div style="display:block;float:left;"> \
      <div v-if="nickname" style="display:flex;align-items:center;"> \
        <div style="display:flex;align-items:center;background:#f7f7f7;padding:6px 8px;border-radius:4px;min-width:220px"> \
          <img :src="headimgurl" width="50px" height="50px"></img> \
          <div style="margin-left:8px;color:#333">{{ nickname }}</div> \
        </div> \
        <a style="margin-left:8px;" href="#" @click="showQRCode=true">点击扫码更换</a> \
      </div> \
      <a v-else href="#" @click="showQRCode=true">点击扫码绑定</a> \
      <div v-if="showQRCode"> \
        <div style="position:absolute;z-index:9998;top:0;left:0;width:100%;height:100vh;background:#000;opacity:0.6;"></div> \
        <div style="position:absolute;z-index:9999;top:0;left:0;height:100vh;width:100%;"> \
          <div style="display:flex;align-items:center;justify-content:center;height:100vh;width:100%;"> \
            <div style="display:flex;flex-direction:column;"> \
              <div><a style="float:right;color:#FFF;margin-bottom:8px;" href="#" @click="showQRCode=false">关闭</a></div> \
              <div id="qrcode"></div> \
            </div> \
          </div> \
        </div> \
      </div> \
    </div>',
    props: ['nickname', 'headimgurl', 'tokenURL', 'checkURL', 'qrcodeChanged'],
    data: function () {
      return {
        headimgurl: null,
        nickname: null,
        showQRCode: false,
        qrcode: null,
        scanInterval: null,
        scanKey: null
      };
    },
    watch: {
      showQRCode: function (val, oldVal) {
        if (val) {
          this.generateQRCode();
          this.startInterval();
        }
        else {
          this.stopInterval();
        }
      }
    },
    methods: {
      generateQRCode: function () {
        if (this.qrcode) return;
        this.$nextTick(function () {
          $.get(this.tokenURL + '?t=' + new Date().valueOf(), function (res) {
            if (res && res.startsWith('https://open.weixin.qq.com/connect/oauth2/authorize')) {
              var qrcode = new QRCode('qrcode');
              qrcode.makeCode(res);
              this.qrcode = qrcode;
              this.scanKey = res.split('state=')[1].split('#')[0];
            }
            else {
              confirm("生成二维码失败");
            }
          }.bind(this));
        }.bind(this));
      },
      stopInterval: function () {
        if (this.scanInterval) clearInterval(this.scanInterval);
      },
      startInterval: function () {
        this.stopInterval();
        this.scanInterval = setInterval(function () {
          if (!this.scanKey) return;
          $.post(this.checkURL + '?key=' + this.scanKey, function (res) {
            if (res.code == 1) {
              this.showQRCode = false;
              this.nickname = res.nickname;
              this.headimgurl = res.headimgurl;
              this.qrcode = null;
              this.qrcodeChanged(this.scanKey);
            }
            else if (res.code == 0) {
              this.showQRCode = false;
              this.qrcode = null;
              confirm('二维码已过期，请重新扫描');
            }
          }.bind(this));
        }.bind(this), 3000);
      }
    },
  });

  $(function () {
    $("input[data-mixtype=bindingwx]").each(function (idx, el) {
      $(el).after('<div id="' + el.id + '_bwx"></div>');
      $(el).hide();
      var data = $(el).data();
      var val = (el.value && JSON.parse(el.value)) || {};
      new BindingWechat({
        propsData: {
          nickname: val.nickname,
          headimgurl: val.headimgurl,
          tokenURL: data.tokenurl,
          checkURL: data.checkurl,
          qrcodeChanged: function(key) {
            $(el).val('changed__' + key);
          }
        }
      }).$mount('#' + el.id + '_bwx');
    });
  });
})(django.jQuery)
