# forms.py - Django custom forms for notification management web interface
#
# Copyright (c) 2020 Jim Fenton
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
from mgmt.models import Method, Rule, Userext
from django import forms
from django.forms.models import modelformset_factory, ModelForm

class SettingsForm(ModelForm):
    class Meta:
        model = Userext
        widgets = {
            'twilio_token': forms.PasswordInput(render_value=True),
            }
        fields = ['email_username', 'email_server', 'email_port', 'email_authentication', 'email_security', 'twilio_sid', 'twilio_token', 'twilio_from']

class MethodForm(ModelForm):
    class Meta:
        model = Method
        fields = ['active', 'name', 'type', 'address', 'preamble',]
                
class RuleMethodField(forms.ModelChoiceField):
	def label_from_instance(self, obj):
		return obj.name

def make_rule_formset(user, extra=1):

	class _RuleForm(forms.ModelForm):
		method = RuleMethodField(
			queryset=Method.objects.filter(user_id=user))
		
		class Meta:
			model = Rule
			fields = ['active', 'priority', 'domain', 'method']
			field_classes = {
				'method' : RuleMethodField,
			}

	return modelformset_factory(Rule, _RuleForm, extra=extra, can_delete=True)
