import matplotlib.pyplot as plt

# Logo-generating module
import logomaker

import sys

#plt.ion()

mat = logomaker.load_mat('crp_sites.fasta', 'fasta',mat_type='frequency')
#mat = logomaker.load_mat('crp_sites.fasta', 'fasta',mat_type='count')

fig = plt.figure(figsize=[8,6])
# Plot information logo
ax = fig.add_subplot(3,1,1)

#logomaker.Logo(mat=mat,mat_type='freq_mat',logo_type='info_logo',color_scheme='random').draw()
logomaker.Logo(mat=mat,mat_type='freq_mat',logo_type='freq_logo').draw()

plt.show()

#plt.tight_layout()
plt.savefig('logo_temp.pdf')

sys.exit()



# Load energy matrix
energy_mat = pd.read_csv('crp_fullwt.26.txt',delim_whitespace=True)
energy_mat.head()

print(energy_mat)

sys.exit()

fig = plt.figure(figsize=[8,6])

# Plot information logo
ax = fig.add_subplot(3,1,1)
logomaker.Logo(mat=energy_mat, mat_type='energy_mat',logo_type='info_logo').draw()
'''
# Plot frequency logo
ax = fig.add_subplot(3,1,2)
logomaker.Logo(mat=energy_mat, mat_type='energy_mat', font_name='Arial Bold',logo_type='freq_logo', color_scheme='random', logo_style='rails',stack_order='small_on_top').draw()

# Plot energy logo
ax = fig.add_subplot(3,1,3)
logomaker.Logo(mat=energy_mat, mat_type='energy_mat',logo_type='energy_logo', neg_flip=True,logo_style='everything', font_name='Comic Sans MS Bold', color_scheme='gray').draw()
'''
#plt.tight_layout()
plt.savefig('logos.pdf')